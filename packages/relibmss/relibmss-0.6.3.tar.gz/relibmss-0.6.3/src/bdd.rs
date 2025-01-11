//

use dd::bdd;
use dd::bdd::Bdd;
use dd::count::*;
use dd::dot::Dot;
use pyo3::exceptions::PyValueError;
use std::collections::HashSet;

use std::cell::RefCell;
use std::collections::HashMap;
use std::rc::Rc;
use std::rc::Weak;

use pyo3::prelude::*;

use crate::bdd_algo;
use crate::interval::Interval;
use crate::bdd_path::BddPath;

#[pyclass(unsendable)]
pub struct BddMgr {
    pub bdd: Rc<RefCell<bdd::Bdd>>,
    pub vars: HashMap<String, bdd::BddNode>,
}

#[pyclass(unsendable)]
#[derive(Clone)]
pub struct BddNode {
    parent: Weak<RefCell<bdd::Bdd>>,
    node: bdd::BddNode,
}

#[pymethods]
impl BddMgr {
    // constructor
    #[new]
    pub fn new() -> Self {
        BddMgr {
            bdd: Rc::new(RefCell::new(bdd::Bdd::new())),
            vars: HashMap::new(),
        }
    }

    // size
    pub fn size(&self) -> (usize, usize, usize) {
        self.bdd.borrow().size()
    }

    // zero
    pub fn zero(&self) -> BddNode {
        BddNode::new(self.bdd.clone(), self.bdd.borrow().zero())
    }

    // one
    pub fn one(&self) -> BddNode {
        BddNode::new(self.bdd.clone(), self.bdd.borrow().one())
    }

    // defvar
    pub fn defvar(&mut self, var: &str) -> BddNode {
        if let Some(node) = self.vars.get(var) {
            return BddNode::new(self.bdd.clone(), node.clone());
        } else {
            let level = self.vars.len();
            let mut bdd = self.bdd.borrow_mut();
            let h = bdd.header(level, var);
            let x0 = bdd.zero();
            let x1 = bdd.one();
            let node = bdd.create_node(&h, &x0, &x1);
            self.vars.insert(var.to_string(), node.clone());
            BddNode::new(self.bdd.clone(), node)
        }
    }

    pub fn var(&self, var: &str) -> Option<BddNode> {
        if let Some(node) = self.vars.get(var) {
            return Some(BddNode::new(self.bdd.clone(), node.clone()));
        } else {
            return None;
        }
    }

    pub fn get_varorder(&self) -> Vec<String> {
        let mut result = vec!["?".to_string(); self.vars.len()];
        for (k,v) in self.vars.iter() {
            let h = v.header().unwrap();
            result[h.level()] = k.clone();
        }
        result
    }

    pub fn rpn(&mut self, expr: &str, vars: HashSet<String>) -> PyResult<BddNode> {
        let mut stack = Vec::new();
        // let mut bdd = self.bdd.borrow_mut();
        for token in expr.split_whitespace() {
            match token {
                "0" | "False" => {
                    let bdd = self.bdd.borrow();
                    stack.push(bdd.zero());
                }
                "1" | "True" => {
                    let bdd = self.bdd.borrow();
                    stack.push(bdd.one());
                }
                "&" => {
                    let mut bdd = self.bdd.borrow_mut();
                    let right = stack.pop().unwrap();
                    let left = stack.pop().unwrap();
                    stack.push(bdd.and(&left, &right));
                }
                "|" => {
                    let mut bdd = self.bdd.borrow_mut();
                    let right = stack.pop().unwrap();
                    let left = stack.pop().unwrap();
                    stack.push(bdd.or(&left, &right));
                }
                "^" => {
                    let mut bdd = self.bdd.borrow_mut();
                    let right = stack.pop().unwrap();
                    let left = stack.pop().unwrap();
                    stack.push(bdd.xor(&left, &right));
                }
                "~" => {
                    let mut bdd = self.bdd.borrow_mut();
                    let node = stack.pop().unwrap();
                    stack.push(bdd.not(&node));
                }
                "?" => {
                    let mut bdd = self.bdd.borrow_mut();
                    let else_ = stack.pop().unwrap();
                    let then = stack.pop().unwrap();
                    let cond = stack.pop().unwrap();
                    stack.push(bdd.ite(&cond, &then, &else_));
                }
                _ => {
                    if let Some(node) = self.vars.get(token) {
                        stack.push(node.clone());
                    } else if let Some(_) = vars.get(token) {
                        let node = self.defvar(token);
                        self.vars.insert(token.to_string(), node.node.clone());
                        stack.push(node.node.clone());
                    } else {
                        return Err(PyValueError::new_err("unknown token"));
                    }
                }
            }
        }
        if let Some(node) = stack.pop() {
            return Ok(BddNode::new(self.bdd.clone(), node));
        } else {
            return Err(PyValueError::new_err("Invalid expression"));
        }
    }

    pub fn ifelse(&self, cond: &BddNode, then: &BddNode, else_: &BddNode) -> BddNode {
        let bdd = self.bdd.clone();
        BddNode::new(
            bdd.clone(),
            bdd.clone()
                .borrow_mut()
                .ite(&cond.node, &then.node, &else_.node),
        )
    }
}

impl BddNode {
    pub fn new(bdd: Rc<RefCell<bdd::Bdd>>, node: bdd::BddNode) -> Self {
        BddNode {
            parent: Rc::downgrade(&bdd),
            node: node,
        }
    }

    pub fn node(&self) -> bdd::BddNode {
        self.node.clone()
    }
}

#[pymethods]
impl BddNode {
    pub fn dot(&self) -> String {
        self.node.dot_string()
    }

    fn __and__(&self, other: &BddNode) -> BddNode {
        let bdd = self.parent.upgrade().unwrap();
        BddNode::new(
            bdd.clone(),
            bdd.clone().borrow_mut().and(&self.node, &other.node),
        )
    }

    fn __or__(&self, other: &BddNode) -> BddNode {
        let bdd = self.parent.upgrade().unwrap();
        BddNode::new(
            bdd.clone(),
            bdd.clone().borrow_mut().or(&self.node, &other.node),
        )
    }

    fn __xor__(&self, other: &BddNode) -> BddNode {
        let bdd = self.parent.upgrade().unwrap();
        BddNode::new(
            bdd.clone(),
            bdd.clone().borrow_mut().xor(&self.node, &other.node),
        )
    }

    fn __invert__(&self) -> BddNode {
        let bdd = self.parent.upgrade().unwrap();
        BddNode::new(bdd.clone(), bdd.clone().borrow_mut().not(&self.node))
    }

    pub fn prob(&self, pv: HashMap<String, f64>) -> f64 {
        let bdd = self.parent.upgrade().unwrap();
        let mut cache = HashMap::new();
        bdd_algo::prob(&mut bdd.clone().borrow_mut(), &self.node, &pv, &mut cache)
    }

    pub fn bmeas(&self, pv: HashMap<String, f64>) -> HashMap<String, f64> {
        let bdd = self.parent.upgrade().unwrap();
        bdd_algo::bmeas(&mut bdd.clone().borrow_mut(), &self.node, &pv)
    }

    pub fn prob_interval(&self, pv: HashMap<String, Interval>) -> Interval {
        let bdd = self.parent.upgrade().unwrap();
        let mut cache = HashMap::new();
        bdd_algo::prob(&mut bdd.clone().borrow_mut(), &self.node, &pv, &mut cache)
    }

    pub fn bmeas_interval(&self, pv: HashMap<String, Interval>) -> HashMap<String, Interval> {
        let bdd = self.parent.upgrade().unwrap();
        bdd_algo::bmeas(&mut bdd.clone().borrow_mut(), &self.node, &pv)
    }

    // obtain minimal path vectors (mpvs) of monotone BDD
    pub fn mpvs(&self) -> BddNode {
        let bdd = self.parent.upgrade().unwrap();
        let mut cache1 = HashMap::new();
        let mut cache2 = HashMap::new();
        let result = bdd_algo::minsol(
            &mut bdd.clone().borrow_mut(),
            &self.node,
            &mut cache1,
            &mut cache2,
        );
        BddNode::new(bdd.clone(), result)
    }

    pub fn extract(&self) -> PyBddPath {
        PyBddPath::new(&self)
    }

    pub fn size(&self) -> (usize, u64) {
        self.node.count()
    }

    pub fn count_set(&self) -> u64 {
        let mut cache = HashMap::new();
        bdd_algo::count_set(&self.node, &mut cache)
    }
}

#[pyclass(unsendable)]
pub struct PyBddPath {
    inner: BddPath,
}

#[pymethods]
impl PyBddPath {
    #[new]
    fn new(root_node: &BddNode) -> Self {
        PyBddPath {
            inner: BddPath::new(&root_node.node),
        }
    }

    fn __len__(&self) -> usize {
        let root = self.inner.root();
        let mut cache: HashMap<usize, u64> = HashMap::new();
        bdd_algo::count_set(&root, &mut cache) as usize
    }

    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<Self>) -> Option<Vec<String>> {
        slf.inner.next()
    }
}