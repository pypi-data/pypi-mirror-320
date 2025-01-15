use winnow::error::ErrMode;
use winnow::stream::{Location, Stream};
use winnow::{
    ascii::{multispace0, till_line_ending},
    combinator::{
        alt, cut_err, delimited, eof, fail, opt, preceded, repeat, separated, separated_pair, seq,
        terminated,
    },
    error::{ContextError, StrContext, StrContextValue},
    token::{any, none_of, one_of, take, take_while},
};
use winnow::{prelude::*, LocatingSlice};

use crate::graph::ScopedGraphError;
use crate::query::MetaQuery;
use crate::{
    graph::{Expr, RawSubject, RelationRef, SubjectRef},
    query::Query,
    tag_graph::TagGraph,
};

pub type Text<'s> = LocatingSlice<&'s str>;

pub fn parse_query(query: &str, validate: bool) -> Result<Query, ScopedGraphError> {
    let (graph, meta_queries) = parse(query)?;
    let query = Query::new(graph, meta_queries)?;
    if validate {
        query.0.validate()?;
    }
    Ok(query)
}

pub fn parse_tag_graph(graph: &str, validate: bool) -> Result<TagGraph, ScopedGraphError> {
    let (graph, _) = parse(graph)?;
    let tag_graph = TagGraph::new(graph)?;
    if validate {
        tag_graph.validate()?;
    }
    Ok(tag_graph)
}

pub(crate) fn parse(query: &str) -> Result<(RawSubject, Vec<MetaQuery>), ScopedGraphError> {
    top_level
        .parse(LocatingSlice::new(query.trim()))
        .map_err(|e| ScopedGraphError::syntax_error(e))
}

fn top_level(input: &mut Text) -> PResult<(RawSubject, Vec<MetaQuery>)> {
    let start = input.location();

    enum Item {
        Expr(Expr),
        Subjects(Vec<RawSubject>),
        MetaQueries(Vec<MetaQuery>),
    }
    let mut item = alt((
        expr.map(Item::Expr),
        subject_body.map(Item::Subjects),
        meta_queries.map(Item::MetaQueries),
        fail.context(StrContext::Expected(StrContextValue::Description(
            "expression",
        )))
        .context(StrContext::Expected(StrContextValue::Description(
            "subject body",
        )))
        .context(StrContext::Expected(StrContextValue::Description(
            "meta queries",
        ))),
    ));
    let mut items = vec![];
    loop {
        multiline0.parse_next(input)?;
        let start = input.checkpoint();
        match item.parse_next(input) {
            Ok(item) => items.push(item),
            Err(ErrMode::Backtrack(e)) => {
                input.reset(&start);
                eof.parse_next(input)
                    .map_err(|_: ErrMode<ContextError>| ErrMode::Backtrack(e))?;
                break;
            }
            Err(e) => return Err(e),
        }
    }

    let mut exprs = vec![];
    let mut children = vec![];
    let mut meta_queries = vec![];
    for item in items {
        match item {
            Item::Expr(expr) => exprs.push(expr),
            Item::Subjects(subjects) => children.extend(subjects),
            Item::MetaQueries(queries) => meta_queries.extend(queries),
        }
    }

    Ok((
        RawSubject {
            name: "".into(),
            identities: vec!["context".into()],
            relation: None,
            expr: Expr::concat(exprs, true),
            children,
            span: start..input.location(),
        },
        meta_queries,
    ))
}

fn whitespace0(input: &mut Text) -> PResult<()> {
    take_while(0.., (' ', '\t')).void().parse_next(input)
}
fn multiline0(input: &mut Text) -> PResult<()> {
    (
        multispace0,
        repeat(0.., (comment, multispace0)).map(|()| ()),
    )
        .void()
        .parse_next(input)
}

fn ws<'s, F, O>(inner: F) -> impl Parser<Text<'s>, O, ContextError>
where
    F: Parser<Text<'s>, O, ContextError>,
{
    delimited(whitespace0, inner, whitespace0)
}
fn paren<'s, F1, F2, O1, O2>(ws: F2, inner: F1) -> impl Parser<Text<'s>, O1, ContextError>
where
    F1: Parser<Text<'s>, O1, ContextError>,
    F2: Parser<Text<'s>, O2, ContextError> + Copy,
{
    preceded(('(', ws), cut_err(delimited(ws, inner, (ws, ')'))))
}

fn meta_queries(input: &mut Text) -> PResult<Vec<MetaQuery>> {
    preceded(
        ('[', whitespace0),
        cut_err(terminated(
            separated(0.., meta_query, ws(',')),
            (']', whitespace0),
        )),
    )
    .parse_next(input)
}
fn meta_query(input: &mut Text) -> PResult<MetaQuery> {
    (opt('-'), separated_pair(tag, ':', tag))
        .map(|(neg, (kind, value))| MetaQuery {
            neg: neg.is_some(),
            kind,
            value,
        })
        .parse_next(input)
}

fn subject_ref(input: &mut Text) -> PResult<SubjectRef> {
    preceded('@', separated(1.., tag, ws('.')))
        .with_span()
        .map(|(path, span)| SubjectRef { path, span })
        .parse_next(input)
}

fn subject(input: &mut Text) -> PResult<RawSubject> {
    let (subject, span) = alt((tag.map(Some), "*".map(|_| None)))
        .context(StrContext::Label("subject"))
        .context(StrContext::Expected(StrContextValue::Description("tag")))
        .with_span()
        .parse_next(input)?;
    let mut identities: Vec<String> = opt(paren(whitespace0, separated(0.., tag, ws(','))))
        .context(StrContext::Label("identities"))
        .parse_next(input)?
        .unwrap_or_default();
    if let Some(subject) = subject.clone() {
        identities.push(subject);
    }

    let name = opt(preceded((whitespace0, '@'), cut_err(tag)))
        .context(StrContext::Label("name"))
        .parse_next(input)?
        .unwrap_or(subject.unwrap_or_else(|| "*".to_owned()));

    let relation = opt(preceded(ws('>'), cut_err(subject_relation)))
        .context(StrContext::Label("relation"))
        .parse_next(input)?;
    let expr = opt(preceded(ws(':'), cut_err(expr))).parse_next(input)?;
    let children = opt(preceded(whitespace0, subject_body))
        .context(StrContext::Label("children"))
        .parse_next(input)?
        .unwrap_or_default();

    Ok(RawSubject {
        name,
        identities,
        relation,
        expr: expr.unwrap_or_default(),
        children,
        span,
    })
}
fn subject_relation(input: &mut Text) -> PResult<RelationRef> {
    seq!(RelationRef {
        target: subject_ref,
        context: opt(paren(whitespace0, subject_ref)),
    })
    .parse_next(input)
}
fn subject_body(input: &mut Text) -> PResult<Vec<RawSubject>> {
    '{'.parse_next(input)?;

    let mut subjects = vec![];
    loop {
        multiline0.parse_next(input)?;
        let start = input.checkpoint();
        match subject.parse_next(input) {
            Ok(subject) => subjects.push(subject),
            Err(ErrMode::Backtrack(_)) => {
                input.reset(&start);
                cut_err('}'.context(StrContext::Expected(StrContextValue::Description("}"))))
                    .parse_next(input)?;
                break;
            }
            Err(e) => return Err(e),
        }
    }
    Ok(subjects)
}

fn expr(input: &mut Text) -> PResult<Expr> {
    separated(1.., or_term, ws(','))
        .context(StrContext::Label("expression"))
        .map(|nodes| Expr::concat(nodes, true))
        .parse_next(input)
}
fn or_term(input: &mut Text) -> PResult<Expr> {
    separated(1.., atom, ws('/'))
        .map(|nodes| Expr::concat(nodes, false))
        .parse_next(input)
}

fn atom(input: &mut Text) -> PResult<Expr> {
    alt((
        tag.with_span().map(|(tag, span)| Expr::Tag(tag, span)),
        neg,
        paren(whitespace0, opt(expr).map(|it| it.unwrap_or_default())),
    ))
    .parse_next(input)
}
fn neg(input: &mut Text) -> PResult<Expr> {
    preceded(('-', whitespace0), atom)
        .map(|e| Expr::Neg(Box::new(e)))
        .parse_next(input)
}

fn tag(input: &mut Text) -> PResult<String> {
    alt((
        tag_plain,
        string,
        fail.context(StrContext::Expected(StrContextValue::Description("tag"))),
    ))
    .parse_next(input)
}

fn tag_plain(input: &mut Text) -> PResult<String> {
    fn is_tag_char(c: char) -> bool {
        c.is_alphanumeric() || c == '·' || c == '\'' || c == '_'
    }
    fn is_tag_char_body(c: char) -> bool {
        is_tag_char(c) || c == '-' || c == ' '
    }
    (one_of(is_tag_char), take_while(0.., is_tag_char_body))
        .take()
        .map(|s: &str| s.trim_ascii_end().to_owned())
        .parse_next(input)
}

fn string(input: &mut Text) -> PResult<String> {
    preceded(
        '\"',
        cut_err(terminated(
            repeat(0.., character).fold(String::new, |mut string, c| {
                string.push(c);
                string
            }),
            '\"',
        )),
    )
    .context(StrContext::Expected("string".into()))
    .parse_next(input)
}

fn character(input: &mut Text) -> PResult<char> {
    let c = none_of('\"').parse_next(input)?;
    if c == '\\' {
        alt((
            any.verify_map(|c| {
                Some(match c {
                    '"' | '\\' | '/' => c,
                    'b' => '\x08',
                    'f' => '\x0C',
                    'n' => '\n',
                    'r' => '\r',
                    't' => '\t',
                    _ => return None,
                })
            }),
            preceded('u', unicode_escape),
        ))
        .parse_next(input)
    } else {
        Ok(c)
    }
}

fn unicode_escape(input: &mut Text) -> PResult<char> {
    alt((
        u16_hex
            .verify(|cp| !(0xD800..0xE000).contains(cp))
            .map(|cp| cp as u32),
        separated_pair(u16_hex, "\\u", u16_hex)
            .verify(|(high, low)| (0xD800..0xDC00).contains(high) && (0xDC00..0xE000).contains(low))
            .map(|(high, low)| {
                let high_ten = (high as u32) - 0xD800;
                let low_ten = (low as u32) - 0xDC00;
                (high_ten << 10) + low_ten + 0x10000
            }),
    ))
    .verify_map(std::char::from_u32)
    .parse_next(input)
}

fn u16_hex(input: &mut Text) -> PResult<u16> {
    take(4usize)
        .verify_map(|s| u16::from_str_radix(s, 16).ok())
        .parse_next(input)
}

fn comment(input: &mut Text) -> PResult<()> {
    ("//", till_line_ending).void().parse_next(input)
}
