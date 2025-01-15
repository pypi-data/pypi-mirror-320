# Generated from ../../../antlr4/align/Align.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .AlignParser import AlignParser
else:
    from AlignParser import AlignParser

# This class defines a complete listener for a parse tree produced by AlignParser.
class AlignListener(ParseTreeListener):

    # Enter a parse tree produced by AlignParser#align.
    def enterAlign(self, ctx:AlignParser.AlignContext):
        pass

    # Exit a parse tree produced by AlignParser#align.
    def exitAlign(self, ctx:AlignParser.AlignContext):
        pass


    # Enter a parse tree produced by AlignParser#operation.
    def enterOperation(self, ctx:AlignParser.OperationContext):
        pass

    # Exit a parse tree produced by AlignParser#operation.
    def exitOperation(self, ctx:AlignParser.OperationContext):
        pass


    # Enter a parse tree produced by AlignParser#condition.
    def enterCondition(self, ctx:AlignParser.ConditionContext):
        pass

    # Exit a parse tree produced by AlignParser#condition.
    def exitCondition(self, ctx:AlignParser.ConditionContext):
        pass


    # Enter a parse tree produced by AlignParser#expression.
    def enterExpression(self, ctx:AlignParser.ExpressionContext):
        pass

    # Exit a parse tree produced by AlignParser#expression.
    def exitExpression(self, ctx:AlignParser.ExpressionContext):
        pass


    # Enter a parse tree produced by AlignParser#subexpression.
    def enterSubexpression(self, ctx:AlignParser.SubexpressionContext):
        pass

    # Exit a parse tree produced by AlignParser#subexpression.
    def exitSubexpression(self, ctx:AlignParser.SubexpressionContext):
        pass


    # Enter a parse tree produced by AlignParser#leftside.
    def enterLeftside(self, ctx:AlignParser.LeftsideContext):
        pass

    # Exit a parse tree produced by AlignParser#leftside.
    def exitLeftside(self, ctx:AlignParser.LeftsideContext):
        pass


    # Enter a parse tree produced by AlignParser#operator.
    def enterOperator(self, ctx:AlignParser.OperatorContext):
        pass

    # Exit a parse tree produced by AlignParser#operator.
    def exitOperator(self, ctx:AlignParser.OperatorContext):
        pass


    # Enter a parse tree produced by AlignParser#negate.
    def enterNegate(self, ctx:AlignParser.NegateContext):
        pass

    # Exit a parse tree produced by AlignParser#negate.
    def exitNegate(self, ctx:AlignParser.NegateContext):
        pass


    # Enter a parse tree produced by AlignParser#exists.
    def enterExists(self, ctx:AlignParser.ExistsContext):
        pass

    # Exit a parse tree produced by AlignParser#exists.
    def exitExists(self, ctx:AlignParser.ExistsContext):
        pass


    # Enter a parse tree produced by AlignParser#foreach.
    def enterForeach(self, ctx:AlignParser.ForeachContext):
        pass

    # Exit a parse tree produced by AlignParser#foreach.
    def exitForeach(self, ctx:AlignParser.ForeachContext):
        pass


    # Enter a parse tree produced by AlignParser#item.
    def enterItem(self, ctx:AlignParser.ItemContext):
        pass

    # Exit a parse tree produced by AlignParser#item.
    def exitItem(self, ctx:AlignParser.ItemContext):
        pass


    # Enter a parse tree produced by AlignParser#duplicate.
    def enterDuplicate(self, ctx:AlignParser.DuplicateContext):
        pass

    # Exit a parse tree produced by AlignParser#duplicate.
    def exitDuplicate(self, ctx:AlignParser.DuplicateContext):
        pass


    # Enter a parse tree produced by AlignParser#variable.
    def enterVariable(self, ctx:AlignParser.VariableContext):
        pass

    # Exit a parse tree produced by AlignParser#variable.
    def exitVariable(self, ctx:AlignParser.VariableContext):
        pass


    # Enter a parse tree produced by AlignParser#command.
    def enterCommand(self, ctx:AlignParser.CommandContext):
        pass

    # Exit a parse tree produced by AlignParser#command.
    def exitCommand(self, ctx:AlignParser.CommandContext):
        pass


    # Enter a parse tree produced by AlignParser#assignment.
    def enterAssignment(self, ctx:AlignParser.AssignmentContext):
        pass

    # Exit a parse tree produced by AlignParser#assignment.
    def exitAssignment(self, ctx:AlignParser.AssignmentContext):
        pass


    # Enter a parse tree produced by AlignParser#valueref.
    def enterValueref(self, ctx:AlignParser.ValuerefContext):
        pass

    # Exit a parse tree produced by AlignParser#valueref.
    def exitValueref(self, ctx:AlignParser.ValuerefContext):
        pass


    # Enter a parse tree produced by AlignParser#key.
    def enterKey(self, ctx:AlignParser.KeyContext):
        pass

    # Exit a parse tree produced by AlignParser#key.
    def exitKey(self, ctx:AlignParser.KeyContext):
        pass


    # Enter a parse tree produced by AlignParser#value.
    def enterValue(self, ctx:AlignParser.ValueContext):
        pass

    # Exit a parse tree produced by AlignParser#value.
    def exitValue(self, ctx:AlignParser.ValueContext):
        pass


    # Enter a parse tree produced by AlignParser#objmap.
    def enterObjmap(self, ctx:AlignParser.ObjmapContext):
        pass

    # Exit a parse tree produced by AlignParser#objmap.
    def exitObjmap(self, ctx:AlignParser.ObjmapContext):
        pass


    # Enter a parse tree produced by AlignParser#array.
    def enterArray(self, ctx:AlignParser.ArrayContext):
        pass

    # Exit a parse tree produced by AlignParser#array.
    def exitArray(self, ctx:AlignParser.ArrayContext):
        pass


    # Enter a parse tree produced by AlignParser#variableref.
    def enterVariableref(self, ctx:AlignParser.VariablerefContext):
        pass

    # Exit a parse tree produced by AlignParser#variableref.
    def exitVariableref(self, ctx:AlignParser.VariablerefContext):
        pass



del AlignParser