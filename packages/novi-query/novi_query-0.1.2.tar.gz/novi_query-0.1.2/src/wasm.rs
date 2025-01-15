use js_sys::Array;
use serde::Serialize;
use serde_wasm_bindgen::to_value;
use std::str;
use wasm_bindgen::prelude::*;

use crate::{graph, parser, query, tag_graph};

// For mysterical reason we can't use js_name since it will produce wrong .d.ts
#[wasm_bindgen]
pub struct Query(query::Query);

#[wasm_bindgen]
impl Query {
    #[wasm_bindgen(js_name = "isMatch")]
    pub fn is_match(&self, graph: &mut TagGraph) -> bool {
        self.0.is_match(&mut graph.0)
    }

    #[wasm_bindgen(js_name = "metaQueries")]
    pub fn meta_queries(&self) -> Result<JsValue, serde_wasm_bindgen::Error> {
        to_value(&self.0 .1)
    }
}

#[derive(Serialize)]
struct PlainError {
    message: String,
    from: usize,
    to: usize,
}

fn convert_error(e: graph::ScopedGraphError) -> JsError {
    let error = PlainError {
        message: e.to_string(),
        from: e.span.start,
        to: e.span.end,
    };
    JsError::new(&serde_json::to_string(&error).unwrap())
}

#[wasm_bindgen(js_name = "parseQuery")]
pub fn parse_query(query: &str, validate: Option<bool>) -> Result<Query, JsError> {
    parser::parse_query(query, validate.unwrap_or(true))
        .map(Query)
        .map_err(convert_error)
}

#[derive(Serialize)]
struct PlainSubject {
    id: u32,
    parent: u32,
    name: String,
    identities: Vec<String>,
    tags: Vec<String>,
}
#[derive(Serialize)]
struct PlainRelation {
    edge: u32,
    source: u32,
    target: u32,
    context: u32,
}

#[wasm_bindgen]
pub struct TagGraph(tag_graph::TagGraph);

#[wasm_bindgen]
impl TagGraph {
    pub fn serialize(
        &self,
        subjects: &Array,
        relations: &Array,
    ) -> Result<(), serde_wasm_bindgen::Error> {
        let graph_relations = match &self.0 {
            tag_graph::TagGraph::Normal(graph) => {
                for subject in graph.subjects.0.iter() {
                    subjects.push(&to_value(&PlainSubject {
                        id: subject.id.0 as u32,
                        parent: subject.parent.0 as u32,
                        name: subject.name.clone(),
                        identities: subject.identities.clone(),
                        tags: subject.extra.tags.clone(),
                    })?);
                }
                &graph.relations
            }
            tag_graph::TagGraph::Indexed(graph) => {
                for subject in graph.graph.subjects.0.iter() {
                    subjects.push(&to_value(&PlainSubject {
                        id: subject.id.0 as u32,
                        parent: subject.parent.0 as u32,
                        name: subject.name.clone(),
                        identities: subject.identities.clone(),
                        tags: subject.extra.tags.iter().cloned().collect(),
                    })?);
                }
                &graph.graph.relations
            }
        };
        for (rel, context) in graph_relations.iter() {
            relations.push(&to_value(&PlainRelation {
                edge: rel.edge.0 as u32,
                source: rel.source.0 as u32,
                target: rel.target.0 as u32,
                context: context.get().0 as u32,
            })?);
        }

        Ok(())
    }
}

#[wasm_bindgen(js_name = "parseTagGraph")]
pub fn parse_tag_graph(graph: &str, validate: Option<bool>) -> Result<TagGraph, JsError> {
    parser::parse_tag_graph(graph, validate.unwrap_or(true))
        .map(TagGraph)
        .map_err(convert_error)
}
