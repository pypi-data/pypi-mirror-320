use std::{
    collections::{HashMap, HashSet},
    hash::Hash,
    mem,
    ops::Range,
};

use crate::graph::{
    Expr, Graph, GraphError, GraphErrorKind, RawSubject, Subject, SubjectExtra, SubjectId, Subjects,
};

fn is_unique<T: Hash + Eq>(mut it: impl Iterator<Item = T>) -> bool {
    let mut set = HashSet::new();
    it.all(|it| set.insert(it))
}

fn validate_identities(identities: &[String], span: &Range<usize>) -> Result<(), GraphError> {
    if !is_unique(identities.iter()) {
        return Err(GraphErrorKind::DuplicateIdentities.with_span(span.clone()));
    }
    Ok(())
}

pub struct Extra {
    pub tags: Vec<String>,
}
impl SubjectExtra for Extra {
    fn from_raw(expr: Expr) -> Result<Self, GraphError> {
        let span = expr.span();
        let tags = match expr {
            Expr::Tag(tag, _) => vec![tag],
            Expr::Group(nodes, true) => nodes
                .into_iter()
                .map(|it| match it {
                    Expr::Tag(tag, _) => Ok(tag),
                    _ => Err(()),
                })
                .collect::<Result<Vec<_>, _>>()
                .map_err(|_| GraphErrorKind::InvalidTags.with_span(span))?,
            _ => return Err(GraphErrorKind::InvalidTags.with_span(span)),
        };
        Ok(Self { tags })
    }

    fn validate(&self, subject: &Subject<Self>) -> Result<(), GraphError> {
        if !is_unique(self.tags.iter()) {
            return Err(GraphErrorKind::DuplicateTags.with_span(subject.span.clone()));
        }
        validate_identities(&subject.identities, &subject.span)?;
        Ok(())
    }
}

pub struct IndexedExtra {
    pub tags: im::HashSet<String>,
    pub dfn_range: Range<u32>,
}
impl SubjectExtra for IndexedExtra {
    fn from_raw(_expr: Expr) -> Result<Self, GraphError> {
        unimplemented!()
    }

    fn validate(&self, subject: &Subject<Self>) -> Result<(), GraphError> {
        validate_identities(&subject.identities, &subject.span)?;
        Ok(())
    }
}

impl IndexedExtra {
    pub(crate) fn match_expr(&self, expr: &Expr) -> bool {
        match expr {
            Expr::Tag(tag, _) => self.tags.contains(tag),
            Expr::Group(nodes, true) => nodes.iter().all(|it| self.match_expr(it)),
            Expr::Group(nodes, false) => nodes.iter().any(|it| self.match_expr(it)),
            Expr::Neg(node) => !self.match_expr(node),
        }
    }

    pub(crate) fn contained_in(&self, range: &Range<u32>) -> bool {
        range.start <= self.dfn_range.start && self.dfn_range.end <= range.end
    }
}

pub struct IndexedTagGraph {
    pub(crate) graph: Graph<IndexedExtra>,
    pub all_subjects: Vec<SubjectId>,
    pub subject_map: HashMap<String, Vec<SubjectId>>,
}

pub enum TagGraph {
    Normal(Graph<Extra>),
    Indexed(IndexedTagGraph),
}
impl TagGraph {
    pub(crate) fn new(subject: RawSubject) -> Result<Self, GraphError> {
        let graph = Graph::from_raw(subject)?;
        Ok(Self::Normal(graph))
    }

    fn collect_ranges(
        subjects: &Subjects<Extra>,
        id: SubjectId,
        mut index: u32,
        result: &mut [Range<u32>],
    ) -> u32 {
        result[id.0].start = index;
        index += 1;
        for child in &subjects[id].children {
            index = Self::collect_ranges(subjects, *child, index, result);
        }
        result[id.0].end = index;
        index
    }

    fn index_graph(mut graph: Graph<Extra>) -> Graph<IndexedExtra> {
        let mut ranges = vec![0..0; graph.len()];
        Self::collect_ranges(&graph.subjects, SubjectId(0), 0, &mut ranges);

        // Parent always contains all tags from children
        let mut tags = vec![im::HashSet::<String>::new(); graph.len()];
        for (i, subject) in graph.subjects.0.iter_mut().enumerate().rev() {
            tags[i] = subject
                .extra
                .tags
                .drain(..)
                .chain(subject.identities.iter().cloned())
                .collect();
            for child in &subject.children {
                let t = mem::take(&mut tags[i]);
                tags[i] = t.union(tags[child.0].clone());
            }
        }

        let extras = tags
            .into_iter()
            .zip(ranges)
            .map(|(tags, range)| IndexedExtra {
                tags,
                dfn_range: range,
            });
        let subjects = graph
            .subjects
            .0
            .into_iter()
            .zip(extras)
            .map(
                |(
                    Subject {
                        id,
                        parent,
                        name,
                        identities,
                        relation,
                        children,
                        span,
                        ..
                    },
                    extra,
                )| {
                    Subject {
                        id,
                        parent,
                        name,
                        identities,
                        relation,
                        children,
                        span,
                        extra,
                    }
                },
            )
            .collect();

        Graph {
            subjects: Subjects(subjects),
            relations: graph.relations,
        }
    }

    pub fn indexed(&mut self) -> &IndexedTagGraph {
        match self {
            Self::Indexed(graph) => graph,
            Self::Normal(_) => {
                let Self::Normal(graph) = mem::replace(
                    self,
                    Self::Normal(Graph {
                        subjects: Subjects(vec![]),
                        relations: HashMap::new(),
                    }),
                ) else {
                    unreachable!()
                };
                let graph = Self::index_graph(graph);

                let mut subject_map = HashMap::<String, Vec<SubjectId>>::new();
                for subject in &graph.subjects.0 {
                    for identity in &subject.identities {
                        subject_map
                            .entry(identity.clone())
                            .or_default()
                            .push(subject.id);
                    }
                }

                let all_subjects = (0..graph.len()).map(SubjectId).collect();

                *self = Self::Indexed(IndexedTagGraph {
                    graph,
                    all_subjects,
                    subject_map,
                });
                let Self::Indexed(graph) = self else {
                    unreachable!()
                };
                graph
            }
        }
    }

    pub fn validate(&self) -> Result<(), GraphError> {
        match self {
            Self::Normal(graph) => graph.validate(),
            Self::Indexed(graph) => graph.graph.validate(),
        }
    }
}
