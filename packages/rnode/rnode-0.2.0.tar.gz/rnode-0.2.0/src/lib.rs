mod types;
mod error;
mod utils;
mod cache;
mod ws_client;
mod nodes;
mod replay;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use std::sync::Arc;
use std::collections::HashMap;
use tokio::runtime::Runtime;
use tracing::{info, error, Level};
use tracing_subscriber::FmtSubscriber;
use std::sync::Once;

use crate::nodes::*;
use crate::ws_client::WsClient;

// 创建一个包装结构体来持有 Runtime
struct ServiceRuntime(tokio::runtime::Runtime);

impl Clone for ServiceRuntime {
    fn clone(&self) -> Self {
        ServiceRuntime(tokio::runtime::Runtime::new().unwrap())
    }
}

#[allow(dead_code)]
struct RNodeService {
    ws_client: Arc<WsClient>,
    runtime: ServiceRuntime,
    total_volume_node: Arc<TotalVolumeNode>,
    mid_price_node: Arc<MidPriceNode>,
    simple_kline_node: Arc<SimpleKlineNode>,
}

// 添加一个静态变量来确保日志只初始化一次
static INIT_LOGGER: Once = Once::new();

fn init_logging() {
    INIT_LOGGER.call_once(|| {
        let subscriber = FmtSubscriber::builder()
            .with_max_level(Level::DEBUG)
            .with_file(true)
            .with_line_number(true)
            .with_thread_ids(true)
            .with_thread_names(true)
            .with_target(false)
            .with_ansi(true)
            .with_env_filter("rnode=debug")
            .try_init();  // 使用 try_init 而不是 init
        
        if let Err(e) = subscriber {
            eprintln!("Failed to initialize logger: {}", e);
        }
    });
}

#[pyclass]
pub struct PyWsClient {
    ws_client: Arc<WsClient>,
    runtime: ServiceRuntime,
}

#[pymethods]
impl PyWsClient {
    #[new]
    fn new(ws_url: String) -> PyResult<Self> {
        init_logging();
        info!("Creating new WebSocket client...");
        
        Ok(Self {
            ws_client: Arc::new(WsClient::new(ws_url)),
            runtime: ServiceRuntime(Runtime::new().unwrap()),
        })
    }

    fn connect(&self, callback: PyObject) -> PyResult<()> {
        let ws_client = self.ws_client.clone();
        let mut receiver = ws_client.get_receiver();
        
        // 启动 WebSocket 连接
        self.runtime.0.block_on(async {
            ws_client.connect().await.map_err(|e| {
                error!("Failed to connect to WebSocket server: {}", e);
                PyErr::new::<pyo3::exceptions::PyConnectionError, _>(e.to_string())
            })?;
            
            info!("Successfully connected to WebSocket server");
            Ok::<(), PyErr>(())
        })?;
        
        // 启动消息处理任务
        self.runtime.0.spawn(async move {
            info!("Starting message receiver task");
            
            while let Ok(msg) = receiver.recv().await {
                info!("Received message: {}", msg);
                Python::with_gil(|py| {
                    match callback.call1(py, (msg,)) {
                        Ok(_) => info!("Callback successful"),
                        Err(e) => error!("Callback failed: {:?}", e),
                    }
                });
            }
        });

        Ok(())
    }

    fn send(&self, message: String) -> PyResult<()> {
        self.runtime.0.block_on(async {
            self.ws_client.send_message(&message).await.map_err(|e| {
                error!("Failed to send message: {}", e);
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
            })
        })
    }

    fn close(&self) -> PyResult<()> {
        self.runtime.0.block_on(async {
            self.ws_client.close().await.map_err(|e| {
                error!("Failed to close connection: {}", e);
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
            })
        })
    }
}

#[pyfunction]
fn init_total_volume_node(
    _py: Python,
    ws_url: String,
    instrument_ids: Vec<String>,
    freq: String,
    callback: PyObject
) -> PyResult<()> {
    // 初始化日志系统
    init_logging();
    info!("Initializing total volume node...");

    let rt = ServiceRuntime(Runtime::new().unwrap());
    let ws_client = Arc::new(WsClient::new(ws_url));
    
    // 连接 WebSocket
    rt.0.block_on(async {
        ws_client.connect().await.map_err(|e| {
            error!("Failed to connect to WebSocket server: {}", e);
            PyErr::new::<pyo3::exceptions::PyConnectionError, _>(e.to_string())
        })?;
        
        let node = TotalVolumeNode::new(
            freq.clone(),
            instrument_ids,
            ws_client.clone()
        );
        
        // 启动节点
        node.start(callback.clone_ref(_py)).await.map_err(|e| {
            error!("Failed to start node: {}", e);
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
        })?;
        
        Ok::<(), PyErr>(())
    })?;

    // 保持 ws_client 和 runtime 活跃
    std::mem::forget(ws_client);
    std::mem::forget(rt);

    Ok(())
}

#[pyfunction]
fn init_mid_price_node(
    _py: Python,
    ws_url: String,
    instrument_ids: Vec<String>,
    freq: String,
    callback: PyObject
) -> PyResult<()> {
    // 初始化日志系统
    init_logging();
    info!("Initializing mid price node...");

    let rt = ServiceRuntime(Runtime::new().unwrap());
    let ws_client = Arc::new(WsClient::new(ws_url));
    
    // 连接 WebSocket
    rt.0.block_on(async {
        ws_client.connect().await.map_err(|e| {
            error!("Failed to connect to WebSocket server: {}", e);
            PyErr::new::<pyo3::exceptions::PyConnectionError, _>(e.to_string())
        })?;
        
        let node = MidPriceNode::new(
            freq.clone(),
            instrument_ids,
            ws_client.clone()
        );
        
        // 启动节点
        node.start(callback.clone_ref(_py)).await.map_err(|e| {
            error!("Failed to start node: {}", e);
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
        })?;
        
        Ok::<(), PyErr>(())
    })?;

    // 保持 ws_client 和 runtime 活跃
    std::mem::forget(ws_client);
    std::mem::forget(rt);

    Ok(())
}

#[pyfunction]
fn init_kline_node(
    _py: Python,
    ws_url: String,
    instrument_ids: Vec<String>,
    freq: String,
    callback: PyObject
) -> PyResult<()> {
    init_logging();
    info!("Initializing kline node...");

    let rt = ServiceRuntime(Runtime::new().unwrap());
    let ws_client = Arc::new(WsClient::new(ws_url.clone()));
    
    rt.0.block_on(async {
        // 连接 WebSocket
        ws_client.connect().await.map_err(|e| {
            error!("Failed to connect to WebSocket server: {}", e);
            PyErr::new::<pyo3::exceptions::PyConnectionError, _>(e.to_string())
        })?;
        
        // 创建并初始化 mid_price_nodes
        let mut mid_price_nodes = HashMap::new();
        for instrument_id in &instrument_ids {
            let mid_price_node = Arc::new(MidPriceNode::new(
                freq.clone(),
                vec![instrument_id.clone()],
                ws_client.clone()
            ));
            
            // 启动 mid_price_node，使用 None 作为回调
            mid_price_node.start(Python::with_gil(|py| Ok::<PyObject, PyErr>(py.None().into_py(py))).unwrap()).await.map_err(|e| {
                error!("Failed to start mid price node: {}", e);
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
            })?;
            
            mid_price_nodes.insert(instrument_id.clone(), mid_price_node);
        }
        
        // 创建并启动 kline node
        let node = SimpleKlineNode::new(
            freq.clone(),
            instrument_ids,
            ws_client.clone(),
            mid_price_nodes
        );
        
        // 只在 kline node 中使用回调
        node.start(callback.clone_ref(_py)).await.map_err(|e| {
            error!("Failed to start kline node: {}", e);
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
        })?;
        
        Ok::<(), PyErr>(())
    })?;

    std::mem::forget(ws_client);
    std::mem::forget(rt);

    Ok(())
}

#[pyfunction]
fn init_resample_kline_node(
    ws_url: String,
    instrument_ids: Vec<String>,
    freq: String,
    callback: PyObject,
) -> PyResult<()> {
    init_logging();
    info!("Initializing resample kline node...");

    let rt = Runtime::new().unwrap();
    let ws_client = Arc::new(WsClient::new(ws_url));

    rt.block_on(async {
        // 连接 WebSocket
        ws_client.connect().await.map_err(|e| {
            error!("Failed to connect to WebSocket server: {}", e);
            PyErr::new::<pyo3::exceptions::PyConnectionError, _>(e.to_string())
        })?;
        info!("Successfully connected to WebSocket server");

        // 创建一个空回调函数
        let empty_callback = Python::with_gil(|py| {
            let locals = pyo3::types::PyDict::new(py);
            py.eval(
                "lambda x: None",  // 使用 lambda 创建一个简单的空函数
                None,
                Some(locals)
            ).unwrap().into_py(py)
        });

        // 初始化基础节点
        let mut kline_nodes = HashMap::new();
        let mut volume_nodes = HashMap::new();
        let mut mid_price_nodes = HashMap::new();

        for instrument_id in &instrument_ids {
            info!("Initializing nodes for {}", instrument_id);
            
            // 初始化 mid_price_node
            let mid_price_node = Arc::new(MidPriceNode::new(
                freq.clone(),
                vec![instrument_id.clone()],
                ws_client.clone()
            ));
            // 启动 mid_price_node
            mid_price_node.start(Python::with_gil(|py| empty_callback.clone_ref(py))).await.map_err(|e| {
                error!("Failed to start mid price node: {}", e);
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
            })?;
            mid_price_nodes.insert(instrument_id.clone(), mid_price_node);
            info!("Started mid price node for {}", instrument_id);

            // 初始化 kline_node
            let kline_node = Arc::new(SimpleKlineNode::new(
                freq.clone(),
                vec![instrument_id.clone()],
                ws_client.clone(),
                mid_price_nodes.clone()
            ));
            // 启动 kline_node
            kline_node.start(Python::with_gil(|py| empty_callback.clone_ref(py))).await.map_err(|e| {
                error!("Failed to start kline node: {}", e);
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
            })?;
            kline_nodes.insert(instrument_id.clone(), kline_node);
            info!("Started kline node for {}", instrument_id);

            // 初始化 volume_node
            let volume_node = Arc::new(TotalVolumeNode::new(
                freq.clone(),
                vec![instrument_id.clone()],
                ws_client.clone()
            ));
            // 启动 volume_node
            volume_node.start(Python::with_gil(|py| empty_callback.clone_ref(py))).await.map_err(|e| {
                error!("Failed to start volume node: {}", e);
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
            })?;
            volume_nodes.insert(instrument_id.clone(), volume_node);
            info!("Started volume node for {}", instrument_id);
        }

        // 创建并启动 resample node
        info!("Creating resample kline node...");
        let node = ResampleKlineNode::new(
            freq.clone(),
            instrument_ids,
            kline_nodes,
            volume_nodes,
            ws_client.clone(),
        );
        
        info!("Starting resample kline node...");
        node.start(callback).await.map_err(|e| {
            error!("Failed to start resample kline node: {}", e);
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
        })?;
        info!("Resample kline node started successfully");

        Ok::<(), PyErr>(())
    })?;

    std::mem::forget(rt);
    std::mem::forget(ws_client);

    Ok(())
}

#[pyfunction]
fn init_resample_kline_node_replay(
    ws_url: String,
    instrument_ids: Vec<String>,
    freq: String,
    callback: PyObject,
    start_time: i64,
    end_time: i64,
    speed_multiplier: f64,
    replay_window: i64,
    x_cur_time: i64,
) -> PyResult<()> {
    init_logging();
    info!("Initializing resample kline node in replay mode...");

    let rt = Runtime::new().unwrap();
    let ws_client = Arc::new(WsClient::with_replay(
        ws_url.clone(),
        start_time,
        end_time,
        speed_multiplier,
        replay_window,
        x_cur_time,
    ));

    rt.block_on(async {
        // 连接 WebSocket
        ws_client.connect().await.map_err(|e| {
            error!("Failed to connect to WebSocket server: {}", e);
            PyErr::new::<pyo3::exceptions::PyConnectionError, _>(e.to_string())
        })?;
        info!("Successfully connected to WebSocket server: {}", ws_url);

        // 创建一个空回调函数
        let empty_callback = Python::with_gil(|py| {
            let locals = pyo3::types::PyDict::new(py);
            py.eval(
                "lambda x: None",  // 使用 lambda 创建一个简单的空函数
                None,
                Some(locals)
            ).unwrap().into_py(py)
        });
        
        // 初始化基础节点
        let mut kline_nodes: HashMap<String, Arc<SimpleKlineNode>> = HashMap::new();
        let mut volume_nodes: HashMap<String, Arc<TotalVolumeNode>> = HashMap::new();
        let mut mid_price_nodes: HashMap<String, Arc<MidPriceNode>> = HashMap::new();

        for instrument_id in &instrument_ids {
            info!("Initializing nodes for {}", instrument_id);
            
            // 初始化 mid_price_node
            let mid_price_node = Arc::new(MidPriceNode::new(
                freq.clone(),
                vec![instrument_id.clone()],
                ws_client.clone()
            ));
            // 启动 mid_price_node
            mid_price_node.start(Python::with_gil(|py| empty_callback.clone_ref(py))).await.map_err(|e| {
                error!("Failed to start mid price node: {}", e);
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
            })?;
            mid_price_nodes.insert(instrument_id.clone(), mid_price_node);
            info!("Started mid price node for {}", instrument_id);

            // 初始化 kline_node
            let kline_node = Arc::new(SimpleKlineNode::new(
                freq.clone(),
                vec![instrument_id.clone()],
                ws_client.clone(),
                mid_price_nodes.clone()
            ));
            // 启动 kline_node
            kline_node.start(Python::with_gil(|py| empty_callback.clone_ref(py))).await.map_err(|e| {
                error!("Failed to start kline node: {}", e);
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
            })?;
            kline_nodes.insert(instrument_id.clone(), kline_node);
            info!("Started kline node for {}", instrument_id);

            // 初始化 volume_node
            let volume_node = Arc::new(TotalVolumeNode::new(
                freq.clone(),
                vec![instrument_id.clone()],
                ws_client.clone()
            ));
            // 启动 volume_node
            volume_node.start(Python::with_gil(|py| empty_callback.clone_ref(py))).await.map_err(|e| {
                error!("Failed to start volume node: {}", e);
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
            })?;
            volume_nodes.insert(instrument_id.clone(), volume_node);
            info!("Started volume node for {}", instrument_id);
        }

        // 创建并启动 resample node
        info!("Creating resample kline node...");
        let node = ResampleKlineNode::new(
            freq,
            instrument_ids,
            kline_nodes,
            volume_nodes,
            ws_client.clone(),
        );
        
        info!("Starting resample kline node...");
        node.start(callback).await.map_err(|e| {
            error!("Failed to start resample kline node: {}", e);
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
        })?;
        info!("Resample kline node started successfully");

        Ok::<(), PyErr>(())
    })?;

    std::mem::forget(rt);
    std::mem::forget(ws_client);

    Ok(())
}

#[pymodule]
fn rnode(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyWsClient>()?;
    m.add_function(wrap_pyfunction!(init_total_volume_node, m)?)?;
    m.add_function(wrap_pyfunction!(init_mid_price_node, m)?)?;
    m.add_function(wrap_pyfunction!(init_kline_node, m)?)?;
    m.add_function(wrap_pyfunction!(init_resample_kline_node, m)?)?;
    m.add_function(wrap_pyfunction!(init_resample_kline_node_replay, m)?)?;
    Ok(())
}
