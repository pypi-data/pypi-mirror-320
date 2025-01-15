use crate::{
    graph::{
        Expr, Graph, GraphError, GraphErrorKind, RawSubject, Relation, RelationContext, Subject,
        SubjectExtra, SubjectId,
    },
    tag_graph::{IndexedTagGraph, TagGraph},
};

pub(crate) struct Extra {
    pub query: Expr,
}
impl SubjectExtra for Extra {
    fn from_raw(query: Expr) -> Result<Self, GraphError> {
        Ok(Self { query })
    }

    fn validate(&self, subject: &Subject<Self>) -> Result<(), GraphError> {
        if subject.identities.len() > 1 {
            return Err(GraphErrorKind::MultipleIdentities.with_span(subject.span.clone()));
        }
        Ok(())
    }
}

#[cfg_attr(feature = "serde", derive(serde::Serialize))]
pub struct MetaQuery {
    pub neg: bool,
    pub kind: String,
    pub value: String,
}

pub struct Query(pub(crate) Graph<Extra>, pub(crate) Vec<MetaQuery>);
impl Query {
    pub(crate) fn new(
        subject: RawSubject,
        meta_queries: Vec<MetaQuery>,
    ) -> Result<Self, GraphError> {
        let graph = Graph::from_raw(subject)?;
        graph.validate()?;
        Ok(Self(graph, meta_queries))
    }

    pub fn meta_queries(&self) -> &[MetaQuery] {
        &self.1
    }

    // TODO: optimize
    fn search(&self, graph: &IndexedTagGraph, id: SubjectId, choices: &mut [SubjectId]) -> bool {
        if id.0 == self.0.len() {
            // Now check relations
            for (rel, context) in &self.0.relations {
                let Some(its_context) = graph.graph.relations.get(&Relation {
                    edge: choices[rel.edge.0],
                    source: choices[rel.source.0],
                    target: choices[rel.target.0],
                }) else {
                    return false;
                };
                let its_context = its_context.get();

                // Only check context if it's explicitly specified in query
                if let RelationContext::Explicit(context) = context {
                    if its_context != choices[context.0] {
                        return false;
                    }
                }
            }
            return true;
        }
        let match_subject = &self.0.subjects[id];
        let parent = &graph.graph.subjects[choices[match_subject.parent.0]];

        let is_relation = match_subject.relation.is_some();

        let alts = if let Some(identity) = match_subject.identities.first() {
            let Some(alts) = graph.subject_map.get(identity) else {
                return false;
            };
            alts
        } else {
            // Matches all subjects
            &graph.all_subjects
        };
        for alt in alts {
            let alt = &graph.graph.subjects[*alt];
            if (!is_relation && !alt.extra.contained_in(&parent.extra.dfn_range))
                || !alt.extra.match_expr(&match_subject.extra.query)
            {
                continue;
            }
            choices[id.0] = alt.id;
            if self.search(graph, SubjectId(id.0 + 1), choices) {
                return true;
            }
        }
        false
    }

    pub fn is_match(&self, graph: &mut TagGraph) -> bool {
        let graph = graph.indexed();
        if !graph
            .graph
            .root()
            .extra
            .match_expr(&self.0.root().extra.query)
        {
            return false;
        }

        let mut choices = vec![SubjectId(0); self.0.len()];
        self.search(graph, SubjectId(1), &mut choices)
    }
}
