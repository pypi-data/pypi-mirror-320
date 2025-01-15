mod sql;

use pyo3::{exceptions::PyValueError, prelude::*, types::PyList};

use crate::{parser, query::Query, tag_graph::TagGraph};

#[pyclass(name = "Query")]
struct QueryWrapper(Query);
#[pymethods]
impl QueryWrapper {
    fn is_match(self_: PyRef<Self>, graph: &mut TagGraphWrapper) -> PyResult<bool> {
        Ok(self_.0.is_match(&mut graph.0))
    }

    fn to_sql<'py>(self_: PyRefMut<'py, Self>, args: Bound<PyList>) -> PyResult<String> {
        sql::to_sql(self_.py(), &self_.0, args)
    }

    fn meta_queries(self_: PyRef<Self>) -> PyResult<Vec<(bool, String, String)>> {
        Ok(self_
            .0
             .1
            .iter()
            .map(|it| (it.neg, it.kind.clone(), it.value.clone()))
            .collect())
    }
}

#[pyfunction]
#[pyo3(signature = (query, validate = true))]
fn parse_query(query: &str, validate: bool) -> PyResult<QueryWrapper> {
    parser::parse_query(query, validate)
        .map(QueryWrapper)
        .map_err(|e| PyValueError::new_err(e.to_string()))
}

#[pyclass(name = "TagGraph")]
struct TagGraphWrapper(TagGraph);
#[pymethods]
impl TagGraphWrapper {
    fn collect_tags(mut self_: PyRefMut<Self>) -> PyResult<Vec<String>> {
        let tags = &self_.0.indexed().graph.root().extra.tags;
        Ok(tags.iter().cloned().collect())
    }
}

#[pyfunction]
#[pyo3(signature = (graph, validate = true))]
fn parse_tag_graph(graph: &str, validate: bool) -> PyResult<TagGraphWrapper> {
    parser::parse_tag_graph(graph, validate)
        .map(TagGraphWrapper)
        .map_err(|e| PyValueError::new_err(e.to_string()))
}

/// This module is implemented in Rust.
#[pymodule]
fn novi_query(m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<QueryWrapper>()?;
    m.add_class::<TagGraphWrapper>()?;
    m.add_function(wrap_pyfunction!(parse_query, m)?)?;
    m.add_function(wrap_pyfunction!(parse_tag_graph, m)?)?;
    Ok(())
}
