use std::sync::Arc;

use pyo3::prelude::*;

use crate::board::Board;
use rust_reversi_core::board::Board as RustBoard;
use rust_reversi_core::search::AlphaBetaSearch as RustAlphaBetaSearch;
use rust_reversi_core::search::{
    Evaluator as RustEvaluator, LegalNumEvaluator as RustLegalNumEvaluator,
    MatrixEvaluator as RustMatrixEvaluator, PieceEvaluator as RustPieceEvaluator,
};

#[derive(Clone)]
struct PyEvaluator {
    py_evaluator: Arc<Py<PyAny>>,
}

impl RustEvaluator for PyEvaluator {
    fn evaluate(&self, board: &RustBoard) -> i32 {
        Python::with_gil(|py| {
            let board_wrapper = Board {
                inner: board.clone(),
            };
            let result = self
                .py_evaluator
                .call_method1(py, "evaluate", (board_wrapper,))
                .expect("Failed to call evaluate method");
            result.extract(py).expect("Failed to extract result")
        })
    }
}

#[derive(Clone)]
enum EvaluatorType {
    Piece(RustPieceEvaluator),
    LegalNum(RustLegalNumEvaluator),
    Matrix(Box<RustMatrixEvaluator>),
    Python(PyEvaluator),
}

impl EvaluatorType {
    fn as_evaluator(&self) -> Box<dyn RustEvaluator> {
        match self {
            EvaluatorType::Piece(e) => Box::new(e.clone()),
            EvaluatorType::LegalNum(e) => Box::new(e.clone()),
            EvaluatorType::Matrix(e) => e.clone(),
            EvaluatorType::Python(e) => Box::new(e.clone()),
        }
    }
}

#[pyclass(subclass)]
#[derive(Clone)]
pub struct Evaluator {
    inner: EvaluatorType,
}

impl Default for Evaluator {
    fn default() -> Self {
        Evaluator {
            inner: EvaluatorType::Piece(RustPieceEvaluator {}),
        }
    }
}

#[pymethods]
impl Evaluator {
    #[new]
    fn new() -> Self {
        Evaluator::default()
    }

    fn set_py_evaluator(&mut self, py_evaluator: Py<PyAny>) {
        self.inner = EvaluatorType::Python(PyEvaluator {
            py_evaluator: Arc::new(py_evaluator),
        });
    }

    fn evaluate(&self, board: &Board) -> i32 {
        self.inner.as_evaluator().evaluate(&board.inner)
    }
}

#[pyclass(extends=Evaluator)]
#[derive(Clone)]
pub struct PieceEvaluator {}

#[pymethods]
impl PieceEvaluator {
    #[new]
    fn new() -> (Self, Evaluator) {
        let evaluator = Evaluator {
            inner: EvaluatorType::Piece(RustPieceEvaluator {}),
        };
        (PieceEvaluator {}, evaluator)
    }
}

#[pyclass(extends=Evaluator)]
pub struct LegalNumEvaluator {}

#[pymethods]
impl LegalNumEvaluator {
    #[new]
    fn new() -> (Self, Evaluator) {
        let evaluator = Evaluator {
            inner: EvaluatorType::LegalNum(RustLegalNumEvaluator {}),
        };
        (LegalNumEvaluator {}, evaluator)
    }
}

#[pyclass(extends=Evaluator)]
pub struct MatrixEvaluator {}

#[pymethods]
impl MatrixEvaluator {
    #[new]
    fn new(matrix: [[i32; 8]; 8]) -> (Self, Evaluator) {
        let evaluator = Evaluator {
            inner: EvaluatorType::Matrix(Box::new(RustMatrixEvaluator::new(matrix))),
        };
        (MatrixEvaluator {}, evaluator)
    }
}

#[pyclass]
pub struct AlphaBetaSearch {
    inner: RustAlphaBetaSearch,
}

#[pymethods]
impl AlphaBetaSearch {
    #[new]
    fn new(evaluator: Evaluator, max_depth: usize) -> Self {
        let rust_evaluator = evaluator.inner;
        AlphaBetaSearch {
            inner: RustAlphaBetaSearch::new(max_depth, rust_evaluator.as_evaluator()),
        }
    }

    fn get_move(&self, board: Board) -> Option<usize> {
        self.inner.get_move(&board.inner)
    }

    fn get_move_with_iter_deepening(&self, board: Board, timeout_ms: u64) -> Option<usize> {
        let timeout = std::time::Duration::from_millis(timeout_ms);
        self.inner
            .get_move_with_iter_deepening(&board.inner, timeout)
    }
}
