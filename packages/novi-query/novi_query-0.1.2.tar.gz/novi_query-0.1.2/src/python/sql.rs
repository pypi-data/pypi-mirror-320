use pyo3::{prelude::*, types::PyList};

use crate::{
    graph::{Expr, GenericExpr},
    query::Query,
};

type RefExpr<'s> = GenericExpr<&'s str>;

fn expr_to_ref<'s>(expr: &'s Expr) -> RefExpr<'s> {
    match expr {
        Expr::Tag(tag, span) => RefExpr::Tag(tag, span.clone()),
        Expr::Group(exprs, ands) => {
            RefExpr::Group(exprs.iter().map(|it| expr_to_ref(it)).collect(), *ands)
        }
        Expr::Neg(expr) => RefExpr::Neg(Box::new(expr_to_ref(expr))),
    }
}

fn bind_arg<'py, T: IntoPyObject<'py>>(args: &Bound<'py, PyList>, value: T) -> PyResult<String> {
    args.append(value)?;
    Ok(format!("${}", args.len()))
}

fn into_generic(expr: RefExpr) -> RefExpr {
    match expr {
        RefExpr::Tag(tag, span) => RefExpr::Tag(tag, span),
        RefExpr::Group(nodes, ands) => {
            let mut new_nodes = Vec::with_capacity(nodes.len());
            for node in nodes {
                let node = into_generic(node);
                if node.is_any() {
                    if !ands {
                        return RefExpr::default();
                    }
                } else {
                    new_nodes.push(node);
                }
            }
            RefExpr::concat(new_nodes, ands)
        }
        RefExpr::Neg(_) => RefExpr::default(),
    }
}

fn join_clauses<S>(clauses: &[S], ands: bool) -> String
where
    S: AsRef<str>,
{
    if clauses.is_empty() {
        return if ands { "true" } else { "false" }.to_owned();
    }
    if clauses.len() == 1 {
        return clauses[0].as_ref().to_owned();
    }

    let join = if ands { " and " } else { " or " };
    let mut clause = format!("({}", clauses[0].as_ref());
    for other in &clauses[1..] {
        clause += join;
        clause += other.as_ref();
    }
    clause.push(')');
    clause
}

fn expr_to_sql<'py>(py: Python<'py>, expr: &RefExpr, args: &Bound<PyList>) -> PyResult<String> {
    Ok(match expr {
        RefExpr::Tag(tag, _) => format!("(tags @> array[{}])", bind_arg(args, tag)?),
        RefExpr::Group(nodes, ands) => {
            let mut plian_tags = vec![];
            let mut others = vec![];
            for node in nodes {
                match node {
                    RefExpr::Tag(tag, _) => plian_tags.push(tag),
                    _ => others.push(expr_to_sql(py, node, args)?),
                }
            }
            if !plian_tags.is_empty() {
                let op = if *ands { "@>" } else { "&&" };
                others.push(format!("(tags {op} {})", bind_arg(args, plian_tags)?));
            }
            join_clauses(&others, *ands)
        }
        RefExpr::Neg(expr) => format!("NOT {}", expr_to_sql(py, expr, args)?),
    })
}

pub fn to_sql<'py>(py: Python<'py>, query: &Query, args: Bound<PyList>) -> PyResult<String> {
    let mut fuzzy_nodes = vec![];
    for subject in query.0.subjects.0.iter().skip(1) {
        fuzzy_nodes.extend(subject.identities.iter().map(|it| RefExpr::Tag(it, 0..0)));
        fuzzy_nodes.push(expr_to_ref(&subject.extra.query));
    }
    let clause = expr_to_sql(py, &into_generic(RefExpr::Group(fuzzy_nodes, true)), &args)?;

    Ok(clause)
}
