use std::collections::HashMap;

use datafusion::config::ConfigOptions;
use datafusion::prelude::{SessionConfig, SessionContext};
use log::debug;
use pyo3::{pyclass, pymethods, PyResult};
use sequila_core::session_context::{SeQuiLaSessionExt, SequilaConfig};

#[pyclass(name = "BioSessionContext")]
#[derive(Clone)]
pub struct PyBioSessionContext {
    pub ctx: SessionContext,
    pub session_config: HashMap<String, String>,
}

#[pymethods]
impl PyBioSessionContext {
    #[pyo3(signature = ())]
    #[new]
    pub fn new() -> PyResult<Self> {
        let ctx = create_context();
        let session_config: HashMap<String, String> = HashMap::new();
        Ok(PyBioSessionContext {
            ctx,
            session_config,
        })
    }
    #[pyo3(signature = (key, value, temporary=Some(false)))]
    pub fn set_option(&mut self, key: &str, value: &str, temporary: Option<bool>) {
        if !temporary.unwrap_or(false) {
            self.session_config
                .insert(key.to_string(), value.to_string());
        }
        set_option_internal(&self.ctx, key, value);
    }

    #[pyo3(signature = ())]
    pub fn sync_options(&mut self) {
        for (key, value) in self.session_config.iter() {
            debug!("Setting option {} to {}", key, value);
            set_option_internal(&self.ctx, key, value);
        }
    }
}

pub fn set_option_internal(ctx: &SessionContext, key: &str, value: &str) {
    let state = ctx.state_ref();
    state
        .write()
        .config_mut()
        .options_mut()
        .set(key, value)
        .unwrap();
}

fn create_context() -> SessionContext {
    let mut options = ConfigOptions::new();
    let tuning_options = vec![
        ("datafusion.optimizer.repartition_joins", "false"),
        ("datafusion.execution.coalesce_batches", "false"),
    ];

    for o in tuning_options {
        options.set(o.0, o.1).expect("TODO: panic message");
    }

    let mut sequila_config = SequilaConfig::default();
    sequila_config.prefer_interval_join = true;

    let config = SessionConfig::from(options)
        .with_option_extension(sequila_config)
        .with_information_schema(true);

    SessionContext::new_with_sequila(config)
}
