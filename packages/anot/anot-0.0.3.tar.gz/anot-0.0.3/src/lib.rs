pub mod annotation;
pub mod cli;
pub mod error;
pub mod input;
pub mod parser;
pub mod python;
pub mod render;

// Re-export main components for easier use
pub use annotation::Annotation;
pub use cli::run;
pub use error::AnotError;
pub use input::{determine_file_type, read_file, FileType};
pub use parser::extract_annotations;
pub use render::RenderAdapter;
