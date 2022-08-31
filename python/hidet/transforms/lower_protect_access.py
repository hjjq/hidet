from typing import Sequence
from hidet.ir import Stmt, Expr, TensorElement, BufferStoreStmt, IfStmt, convert
from hidet.ir.dialects.lowlevel import TensorPointerType
from hidet.ir.expr import And, IfThenElse
from hidet.ir.type import TensorType
from hidet.transforms.base import Pass, FunctionBodyPass
from hidet.ir.functors import StmtExprRewriter, infer_type


def bound_checking_condition(buf: Expr, indices: Sequence[Expr]) -> Expr:
    shape = get_buffer_shape(buf)
    conditions = []
    for idx, extent in zip(indices, shape):
        conditions.append(And(0 <= idx, idx < extent))
    return And.join_list(conditions)


def get_buffer_shape(buf: Expr):
    buf_type = infer_type(buf)
    if isinstance(buf_type, TensorType):
        return buf_type.shape
    elif isinstance(buf_type, TensorPointerType):
        return buf_type.tensor_type.shape
    else:
        raise ValueError('Expect TensorType or TensorPointerType, got {}'.format(buf_type))


class LowerProtectAccessRewriter(StmtExprRewriter):
    def visit_TensorElement(self, e: TensorElement):
        if e.protected:
            base = self.visit(e.base)
            indices = [self.visit(v) for v in e.indices]
            return IfThenElse(
                cond=bound_checking_condition(base, indices),
                then_expr=TensorElement(base, indices, protected=False),
                else_expr=convert(0.0, dtype=infer_type(e))
            )
        else:
            return StmtExprRewriter.visit_TensorElement(self, e)

    def visit_BufferStoreStmt(self, stmt: BufferStoreStmt):
        if stmt.protected:
            buf = self.visit(stmt.buf)
            indices = [self.visit(v) for v in stmt.indices]
            value = self.visit(stmt.value)
            return IfStmt(
                cond=bound_checking_condition(buf, indices),
                then_body=BufferStoreStmt(
                    buf=buf,
                    indices=indices,
                    protected=False,
                    value=value
                )
            )
        else:
            return StmtExprRewriter.visit_BufferStoreStmt(self, stmt)


class LowerProtectAccessPass(FunctionBodyPass):
    def process_body(self, stmt: Stmt) -> Stmt:
        rewriter = LowerProtectAccessRewriter()
        return rewriter.rewrite(stmt)


def lower_protect_access_pass() -> Pass:
    return LowerProtectAccessPass()
