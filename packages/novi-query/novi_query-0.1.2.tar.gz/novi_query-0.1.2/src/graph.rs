use std::{
    collections::HashMap,
    fmt, mem,
    ops::{Index, IndexMut, Range},
};
use winnow::{
    error::{ContextError, ParseError},
    LocatingSlice,
};

pub type GraphError = ScopedGraphError<'static>;

#[derive(Debug)]
pub struct ScopedGraphError<'s> {
    pub kind: GraphErrorKind<'s>,
    pub span: Range<usize>,
}
impl fmt::Display for ScopedGraphError<'_> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "({}, {}): {}",
            self.span.start, self.span.end, self.kind
        )
    }
}
impl std::error::Error for ScopedGraphError<'_> {}
impl<'s> ScopedGraphError<'s> {
    pub fn syntax_error(e: ParseError<LocatingSlice<&'s str>, ContextError>) -> Self {
        let span = e.offset()..e.offset() + 1;
        Self {
            kind: GraphErrorKind::SyntaxError(e),
            span,
        }
    }
}

#[derive(Debug)]
pub enum GraphErrorKind<'s> {
    SyntaxError(ParseError<LocatingSlice<&'s str>, ContextError>),

    SubjectNotFound(String),
    NestedRelation,
    MultipleIdentities,

    DuplicateIdentities,
    DuplicateTags,
    DuplicateRelations,

    InvalidTags,
}
impl fmt::Display for GraphErrorKind<'_> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            GraphErrorKind::SyntaxError(e) => write!(f, "invalid syntax\n{e}"),
            GraphErrorKind::SubjectNotFound(subject) => write!(f, "subject not found: {subject}"),
            GraphErrorKind::NestedRelation => write!(
                f,
                "relation's source, target & context cannot be another relation"
            ),
            GraphErrorKind::MultipleIdentities => write!(f, "can only query one identity"),
            GraphErrorKind::DuplicateIdentities => write!(f, "duplicate identities"),
            GraphErrorKind::DuplicateTags => write!(f, "duplicate tags"),
            GraphErrorKind::DuplicateRelations => write!(f, "duplicate relations"),
            GraphErrorKind::InvalidTags => write!(f, "invalid tags"),
        }
    }
}
impl<'s> GraphErrorKind<'s> {
    pub fn with_span(self, span: Range<usize>) -> ScopedGraphError<'s> {
        ScopedGraphError { kind: self, span }
    }
}

#[derive(Debug, Default, Clone, Copy, Hash, PartialEq, Eq, PartialOrd, Ord)]
#[repr(transparent)]
pub struct SubjectId(pub usize);

pub struct Subjects<E>(pub(crate) Vec<Subject<E>>);
impl<E: SubjectExtra> Index<SubjectId> for Subjects<E> {
    type Output = Subject<E>;

    fn index(&self, index: SubjectId) -> &Self::Output {
        &self.0[index.0]
    }
}
impl<E: SubjectExtra> IndexMut<SubjectId> for Subjects<E> {
    fn index_mut(&mut self, index: SubjectId) -> &mut Self::Output {
        &mut self.0[index.0]
    }
}

struct ResolveContext<'a, E> {
    subjects: &'a Subjects<E>,
    relation_refs: &'a [Option<RelationRef>],
    current_context: SubjectId,
    parent: SubjectId,
    ref_map: HashMap<&'a str, SubjectId>,
}
impl<E: SubjectExtra> ResolveContext<'_, E> {
    fn unknown_subject(subject: &SubjectRef) -> GraphError {
        GraphErrorKind::SubjectNotFound(subject.path.join(".")).with_span(subject.span.clone())
    }

    fn resolve_subject(&self, subject: &SubjectRef) -> Result<SubjectId, GraphError> {
        let mut it = subject.path.iter();
        let Some(mut n) = self.ref_map.get(it.next().unwrap().as_str()).copied() else {
            return Err(Self::unknown_subject(subject));
        };
        for i in it {
            match self.subjects[n]
                .children
                .iter()
                .rev()
                .find(|c| &self.subjects[**c].name == i)
            {
                Some(id) => n = *id,
                None => return Err(Self::unknown_subject(subject)),
            };
        }

        Ok(n)
    }
}
struct ResolveResult<'a> {
    relations: &'a mut HashMap<Relation, RelationContext>,
    relation_tuples: &'a mut [Option<(SubjectId, SubjectId)>],
}

#[derive(Debug, Clone, Hash, PartialEq, Eq)]
pub struct Relation {
    pub edge: SubjectId,
    pub source: SubjectId,
    pub target: SubjectId,
}

pub enum RelationContext {
    Explicit(SubjectId),
    Implicit(SubjectId),
}
impl RelationContext {
    pub fn get(&self) -> SubjectId {
        match self {
            RelationContext::Explicit(id) => *id,
            RelationContext::Implicit(id) => *id,
        }
    }
}

#[derive(Debug)]
pub(crate) struct RawSubject {
    pub name: String,
    pub identities: Vec<String>,
    pub relation: Option<RelationRef>,
    pub expr: Expr,
    pub children: Vec<RawSubject>,
    pub span: Range<usize>,
}
impl RawSubject {
    fn flatten_into<E: SubjectExtra>(
        mut self,
        subjects: &mut Subjects<E>,
        relations: &mut Vec<Option<RelationRef>>,
        parent: Option<SubjectId>,
    ) -> Result<SubjectId, GraphError> {
        let children = mem::take(&mut self.children);
        let id = SubjectId(subjects.0.len());

        let subject = Subject {
            id,
            parent: parent.unwrap_or_default(),
            name: self.name,
            identities: self.identities,
            relation: None,
            children: vec![],
            span: self.span,
            extra: E::from_raw(self.expr)?,
        };
        subjects.0.push(subject);
        relations.push(self.relation);
        subjects[id].children = children
            .into_iter()
            .map(|it| it.flatten_into(subjects, relations, Some(id)))
            .collect::<Result<Vec<_>, _>>()?;

        Ok(id)
    }
}

pub trait SubjectExtra: Sized {
    fn from_raw(expr: Expr) -> Result<Self, GraphError>;
    fn validate(&self, subject: &Subject<Self>) -> Result<(), GraphError>;
}

#[derive(Debug)]
pub struct Subject<E> {
    pub id: SubjectId,
    pub parent: SubjectId,
    pub name: String,
    pub identities: Vec<String>,
    pub relation: Option<(SubjectId, SubjectId)>,
    pub children: Vec<SubjectId>,
    pub span: Range<usize>,

    pub extra: E,
}
impl<E: SubjectExtra> Subject<E> {
    fn resolve(
        &self,
        cx: &ResolveContext<E>,
        result: &mut ResolveResult,
    ) -> Result<(), GraphError> {
        if let Some(rel) = &cx.relation_refs[self.id.0] {
            let source = cx.parent;
            let target = cx.resolve_subject(&rel.target)?;
            let context = match &rel.context {
                Some(c) => RelationContext::Explicit(cx.resolve_subject(c)?),
                None => RelationContext::Implicit(cx.current_context),
            };

            if cx.subjects[source].relation.is_some()
                || cx.subjects[target].relation.is_some()
                || cx.subjects[context.get()].relation.is_some()
            {
                return Err(GraphErrorKind::NestedRelation.with_span(self.span.clone()));
            }

            result.relation_tuples[self.id.0] = Some((source, target));
            if context.get() != cx.parent
                && result
                    .relations
                    .insert(
                        Relation {
                            edge: self.id,
                            source,
                            target,
                        },
                        context,
                    )
                    .is_some()
            {
                return Err(GraphErrorKind::DuplicateRelations.with_span(self.span.clone()));
            }
        }

        if self.children.is_empty() {
            return Ok(());
        }

        let self_is_context = self.identities.iter().any(|it| it == "context");
        let current_context = if self_is_context {
            self.id
        } else {
            cx.current_context
        };

        let mut cx = ResolveContext {
            subjects: cx.subjects,
            relation_refs: cx.relation_refs,
            current_context,
            parent: self.id,
            ref_map: cx.ref_map.clone(),
        };
        for &child in &self.children {
            cx.ref_map.insert(&cx.subjects[child].name, child);
        }
        for &child in &self.children {
            cx.subjects[child].resolve(&cx, result)?;
        }

        Ok(())
    }

    fn validate(&self, subjects: &Subjects<E>) -> Result<(), GraphError> {
        self.extra.validate(self)?;
        for &child in &self.children {
            subjects[child].validate(subjects)?;
        }
        Ok(())
    }
}

#[derive(Debug)]
pub struct RelationRef {
    pub target: SubjectRef,
    pub context: Option<SubjectRef>,
}

#[derive(Debug)]
pub struct SubjectRef {
    pub path: Vec<String>,
    pub span: Range<usize>,
}

#[derive(Debug)]
pub enum GenericExpr<S> {
    Tag(S, Range<usize>),
    Group(Vec<GenericExpr<S>>, bool),
    Neg(Box<GenericExpr<S>>),
}
impl<S> Default for GenericExpr<S> {
    fn default() -> Self {
        Self::Group(vec![], true)
    }
}
impl<S> GenericExpr<S> {
    pub fn span(&self) -> Range<usize> {
        match self {
            Self::Tag(_, span) => span.clone(),
            Self::Group(nodes, _) => {
                if nodes.is_empty() {
                    return 0..0;
                }
                let first = nodes[0].span();
                let last = nodes[nodes.len() - 1].span();
                first.start..last.end
            }
            Self::Neg(node) => {
                let span = node.span();
                (span.start - 1)..span.end
            }
        }
    }

    pub fn concat(nodes: Vec<GenericExpr<S>>, ands: bool) -> Self {
        let mut result = vec![];
        for node in nodes {
            match node {
                GenericExpr::Group(nodes, its_ands) if its_ands == ands => {
                    result.extend(nodes);
                }
                _ => result.push(node),
            }
        }
        if result.len() == 1 {
            result.remove(0)
        } else {
            Self::Group(result, ands)
        }
    }

    pub fn is_any(&self) -> bool {
        matches!(self, Self::Group(nodes, false) if nodes.is_empty())
    }
}

pub type Expr = GenericExpr<String>;

pub struct Graph<E> {
    pub subjects: Subjects<E>,
    pub relations: HashMap<Relation, RelationContext>,
}
impl<E: SubjectExtra> Graph<E> {
    pub(crate) fn from_raw(subject: RawSubject) -> Result<Self, GraphError> {
        let mut subjects = Subjects(vec![]);
        let mut relation_refs = vec![];
        subject.flatten_into(&mut subjects, &mut relation_refs, None)?;

        let mut relations = HashMap::new();
        let mut relation_tuples = vec![None; subjects.0.len()];
        subjects[SubjectId(0)].resolve(
            &ResolveContext {
                subjects: &subjects,
                relation_refs: &relation_refs,
                current_context: SubjectId(0),
                parent: SubjectId(0),
                ref_map: HashMap::new(),
            },
            &mut ResolveResult {
                relations: &mut relations,
                relation_tuples: &mut relation_tuples,
            },
        )?;

        for (subject, rel) in subjects.0.iter_mut().zip(relation_tuples) {
            subject.relation = rel;
        }
        for (Relation { edge, source, .. }, context) in &relations {
            // TODO: optimize
            let children = &mut subjects[*source].children;
            children.remove(children.binary_search(edge).unwrap());
            subjects[context.get()].children.push(*edge);
        }

        Ok(Self {
            subjects,
            relations,
        })
    }

    pub fn root(&self) -> &Subject<E> {
        &self.subjects[SubjectId(0)]
    }

    pub fn len(&self) -> usize {
        self.subjects.0.len()
    }

    pub fn validate(&self) -> Result<(), GraphError> {
        self.root().validate(&self.subjects)
    }
}
