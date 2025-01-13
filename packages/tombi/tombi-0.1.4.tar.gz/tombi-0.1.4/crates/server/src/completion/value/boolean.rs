use schema_store::BooleanSchema;

use crate::completion::FindCompletionItems;

impl FindCompletionItems for BooleanSchema {
    fn find_completion_items(
        &self,
        _accessors: &[schema_store::Accessor],
        _definitions: &schema_store::SchemaDefinitions,
        _completion_hint: Option<crate::completion::CompletionHint>,
    ) -> (
        Vec<tower_lsp::lsp_types::CompletionItem>,
        Vec<schema_store::Error>,
    ) {
        if let Some(enumerate) = &self.enumerate {
            let items = enumerate
                .iter()
                .map(|value| tower_lsp::lsp_types::CompletionItem {
                    label: value.to_string(),
                    kind: Some(tower_lsp::lsp_types::CompletionItemKind::VALUE),
                    ..Default::default()
                })
                .collect();
            return (items, Vec::with_capacity(0));
        } else {
            (
                ["true", "false"]
                    .into_iter()
                    .map(|label| tower_lsp::lsp_types::CompletionItem {
                        label: label.to_string(),
                        kind: Some(tower_lsp::lsp_types::CompletionItemKind::VALUE),
                        ..Default::default()
                    })
                    .collect(),
                Vec::with_capacity(0),
            )
        }
    }
}
