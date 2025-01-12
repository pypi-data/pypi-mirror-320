from dataclasses import replace
from typing import Optional, Union

from antlr4 import ParserRuleContext

from txt2musicxml.enums import Barline, get_barline_from_text
from txt2musicxml.grammer.ChordsParser import ChordsParser
from txt2musicxml.grammer.ChordsVisitor import ChordsVisitor
from txt2musicxml.models import (
    Alteration,
    Bar,
    Bass,
    BassAlteration,
    BassNote,
    Chord,
    KeySignature,
    Line,
    Root,
    RootAlteration,
    RootNote,
    Sheet,
    Slash,
    Suffix,
    TimeSignature,
)


class ConcreteChordsVisitor(ChordsVisitor):
    curr_time_signature: TimeSignature = TimeSignature()
    latest_key_signature: Optional[KeySignature] = None

    # Visit a parse tree produced by ChordsParser#sheet.
    def visitSheet(self, ctx: ChordsParser.SheetContext) -> Sheet:
        lines_ctx = ctx.line()
        lines = [self.visit(line) for line in lines_ctx]
        return Sheet(lines)

    # Visit a parse tree produced by ChordsParser#line.
    def visitLine(self, ctx: ChordsParser.LineContext) -> Line:
        bars_ctx = ctx.bar()
        bars = [self.visit(bar) for bar in bars_ctx]
        return Line(bars)

    # Visit a parse tree produced by ChordsParser#bar.
    def visitBar(self, ctx: ChordsParser.BarContext) -> Bar:
        rehearsal_mark_ctx = ctx.REHEARSAL()
        rehearsal_mark: Optional[str] = None
        if rehearsal_mark_ctx:
            rehearsal_mark = rehearsal_mark_ctx.getText()[
                1:-1
            ]  # strip brackets []
        key_signature_ctx = ctx.alteration()
        key_signature: Optional[KeySignature] = None
        if key_signature_ctx:
            key_signature = self.visit(key_signature_ctx)
            self.latest_key_signature = key_signature
        time_signature_ctx = ctx.TIME_SIGNATURE()
        time_signature = self.curr_time_signature
        if time_signature_ctx:
            numerator, denominator = time_signature_ctx.getText().split("/")
            time_signature = TimeSignature(
                int(numerator), int(denominator), should_print=True
            )
            self.curr_time_signature = replace(
                time_signature, should_print=False
            )
        chords_ctx = ctx.chord_or_slash()
        measure_repeat_ctx = ctx.MEASURE_REPEAT()
        right_barline = self.visit(ctx.right_barlines())
        if chords_ctx:
            chords = [self.visit(chord) for chord in chords_ctx]
            return Bar(
                chords=chords,
                right_barline=right_barline,
                timesignature=time_signature,
                rehearsal_mark=rehearsal_mark,
                key_signature=key_signature,
                latest_key_signature=self.latest_key_signature,
            )
        elif measure_repeat_ctx:
            return Bar(measure_repeat=True, right_barline=right_barline)
        return Bar()  # satisfies mypy, will never be called

    def visitRight_barlines(
        self, ctx: ChordsParser.Right_barlinesContext
    ) -> Barline:
        barline_text = ctx.getText()
        return get_barline_from_text(barline_text)

    # Visit a parse tree produced by ChordsParser#chord.
    def visitChord(self, ctx: ChordsParser.ChordContext) -> Chord:
        root_ctx = ctx.root()
        root = self.visit(root_ctx) if root_ctx else None
        suffix_ctx = ctx.suffix()
        suffix = self.visit(suffix_ctx) if suffix_ctx else None
        bass_ctx = ctx.bass()
        bass = self.visit(bass_ctx) if bass_ctx else None
        return Chord(root, suffix, bass)  # type: ignore

    def visitSlash(self, ctx: ChordsParser.SlashContext):
        return Slash()

    # Visit a parse tree produced by ChordsParser#root.
    def visitRoot(self, ctx: ChordsParser.RootContext) -> Root:
        note = self.visit(ctx.note())
        alteration_ctx = ctx.alteration()
        alteration = self.visit(alteration_ctx) if alteration_ctx else None
        return Root(note, alteration)

    # Visit a parse tree produced by ChordsParser#bass.
    def visitBass(self, ctx: ChordsParser.BassContext) -> Bass:
        note = self.visit(ctx.note())
        alteration_ctx = ctx.alteration()
        alteration = self.visit(alteration_ctx) if alteration_ctx else None
        return Bass(note, alteration)

    # Visit a parse tree produced by ChordsParser#note.
    def visitNote(
        self, ctx: ChordsParser.NoteContext
    ) -> Union[RootNote, BassNote]:
        if self._is_child_of_root_ctx(ctx):
            return RootNote(ctx.getText())
        if self._is_child_of_bass_ctx(ctx):
            return BassNote(ctx.getText())
        raise

    # Visit a parse tree produced by ChordsParser#alteration.
    def visitAlteration(
        self, ctx: ChordsParser.AlterationContext
    ) -> Alteration:
        if self._is_child_of_root_ctx(ctx):
            return RootAlteration(ctx.getText())
        if self._is_child_of_bass_ctx(ctx):
            return BassAlteration(ctx.getText())
        if self._is_child_of(ctx, ChordsParser.BarContext):
            return KeySignature(ctx.getText())
        raise  # It must be one of them. rasing to satisfy type checker

    # Visit a parse tree produced by ChordsParser#suffix.
    def visitSuffix(self, ctx: ChordsParser.SuffixContext) -> Suffix:
        return Suffix(ctx.getText())

    def _is_child_of_root_ctx(self, ctx: ParserRuleContext) -> bool:
        return self._is_child_of(ctx, ChordsParser.RootContext)

    def _is_child_of_bass_ctx(self, ctx: ParserRuleContext) -> bool:
        return self._is_child_of(ctx, ChordsParser.BassContext)

    @staticmethod
    def _is_child_of(
        ctx: ParserRuleContext, parent_ctx: type[ParserRuleContext]
    ):
        return isinstance(ctx.parentCtx, parent_ctx)
