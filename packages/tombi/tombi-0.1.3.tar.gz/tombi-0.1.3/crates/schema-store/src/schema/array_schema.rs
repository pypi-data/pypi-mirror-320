use std::sync::{Arc, RwLock};

use crate::Accessor;

use super::{FindCandidates, Referable, SchemaDefinitions, ValueSchema};

#[derive(Debug, Default, Clone)]
pub struct ArraySchema {
    pub title: Option<String>,
    pub description: Option<String>,
    pub items: Option<Arc<RwLock<Referable<ValueSchema>>>>,
    pub min_items: Option<usize>,
    pub max_items: Option<usize>,
    pub unique_items: Option<bool>,
    pub default: Option<Vec<serde_json::Value>>,
}

impl ArraySchema {
    pub fn new(object: &serde_json::Map<String, serde_json::Value>) -> Self {
        Self {
            title: object
                .get("title")
                .and_then(|v| v.as_str().map(|s| s.to_string())),
            description: object
                .get("description")
                .and_then(|v| v.as_str().map(|s| s.to_string())),
            items: object.get("items").and_then(|value| {
                value
                    .as_object()
                    .and_then(Referable::<ValueSchema>::new)
                    .map(|schema| Arc::new(RwLock::new(schema)))
            }),
            min_items: object
                .get("minItems")
                .and_then(|v| v.as_u64().map(|n| n as usize)),
            max_items: object
                .get("maxItems")
                .and_then(|v| v.as_u64().map(|n| n as usize)),
            unique_items: object.get("uniqueItems").and_then(|v| v.as_bool()),
            default: object
                .get("default")
                .and_then(|v| v.as_array().map(|arr| arr.clone())),
        }
    }
}

impl FindCandidates for ArraySchema {
    fn find_candidates(
        &self,
        accessors: &[Accessor],
        definitions: &SchemaDefinitions,
    ) -> (Vec<ValueSchema>, Vec<crate::Error>) {
        let mut errors = Vec::new();
        let mut candidates = Vec::new();

        if let Some(Ok(mut items)) = self.items.as_ref().map(|items| items.write()) {
            if let Ok(value_schema) = items.resolve(definitions) {
                let (mut item_candidates, mut item_errors) =
                    value_schema.find_candidates(&accessors[1..], definitions);
                candidates.append(&mut item_candidates);
                errors.append(&mut item_errors);
            }
        }

        (candidates, errors)
    }
}
