mod all_of;
mod any_of;
mod one_of;

use super::{CompletionCandidate, CompletionHint, FindCompletionItems};
use schema_store::{
    Accessor, ArraySchema, BooleanSchema, FloatSchema, IntegerSchema, LocalDateSchema,
    LocalDateTimeSchema, LocalTimeSchema, OffsetDateTimeSchema, SchemaDefinitions, StringSchema,
    TableSchema, ValueSchema,
};
use tower_lsp::lsp_types::CompletionItem;

impl FindCompletionItems for ValueSchema {
    fn find_completion_items(
        &self,
        accessors: &[Accessor],
        definitions: &SchemaDefinitions,
        completion_hint: Option<CompletionHint>,
    ) -> (Vec<CompletionItem>, Vec<schema_store::Error>) {
        match self {
            Self::Table(table) => {
                table.find_completion_items(accessors, definitions, completion_hint)
            }
            Self::AllOf(all_of) => {
                all_of.find_completion_items(accessors, definitions, completion_hint)
            }
            Self::AnyOf(any_of) => {
                any_of.find_completion_items(accessors, definitions, completion_hint)
            }
            Self::OneOf(one_of) => {
                one_of.find_completion_items(accessors, definitions, completion_hint)
            }
            _ => (Vec::new(), Vec::new()),
        }
    }
}

impl CompletionCandidate for ValueSchema {
    fn title(
        &self,
        definitions: &SchemaDefinitions,
        completion_hint: Option<CompletionHint>,
    ) -> Option<String> {
        match self {
            Self::Boolean(BooleanSchema { title, .. })
            | Self::Integer(IntegerSchema { title, .. })
            | Self::Float(FloatSchema { title, .. })
            | Self::String(StringSchema { title, .. })
            | Self::OffsetDateTime(OffsetDateTimeSchema { title, .. })
            | Self::LocalDateTime(LocalDateTimeSchema { title, .. })
            | Self::LocalDate(LocalDateSchema { title, .. })
            | Self::LocalTime(LocalTimeSchema { title, .. })
            | Self::Array(ArraySchema { title, .. })
            | Self::Table(TableSchema { title, .. }) => title.as_deref().map(ToString::to_string),
            Self::OneOf(one_of) => one_of.title(definitions, completion_hint),
            Self::AnyOf(any_of) => any_of.title(definitions, completion_hint),
            Self::AllOf(all_of) => all_of.title(definitions, completion_hint),
            Self::Null => None,
        }
    }

    fn description(
        &self,
        definitions: &SchemaDefinitions,
        completion_hint: Option<CompletionHint>,
    ) -> Option<String> {
        match self {
            Self::Boolean(BooleanSchema { description, .. })
            | Self::Integer(IntegerSchema { description, .. })
            | Self::Float(FloatSchema { description, .. })
            | Self::String(StringSchema { description, .. })
            | Self::OffsetDateTime(OffsetDateTimeSchema { description, .. })
            | Self::LocalDateTime(LocalDateTimeSchema { description, .. })
            | Self::LocalDate(LocalDateSchema { description, .. })
            | Self::LocalTime(LocalTimeSchema { description, .. })
            | Self::Array(ArraySchema { description, .. })
            | Self::Table(TableSchema { description, .. }) => {
                description.as_deref().map(ToString::to_string)
            }
            Self::OneOf(one_of) => one_of.description(definitions, completion_hint),
            Self::AnyOf(any_of) => any_of.description(definitions, completion_hint),
            Self::AllOf(all_of) => all_of.description(definitions, completion_hint),
            Self::Null => None,
        }
    }
}
