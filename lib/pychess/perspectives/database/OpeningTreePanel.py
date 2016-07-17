# -*- coding: UTF-8 -*-
from __future__ import print_function

from gi.repository import Gtk, GObject

from pychess.Utils.lutils.lmovegen import genAllMoves
from pychess.Utils.lutils.LBoard import LBoard
from pychess.Utils.lutils.lmove import toSAN
from pychess.Utils.const import FEN_START


class OpeningTreePanel(Gtk.TreeView):
    def __init__(self, gamelist):
        GObject.GObject.__init__(self)
        self.gamelist = gamelist

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.liststore = Gtk.ListStore(int, str, int, int)
        self.modelsort = Gtk.TreeModelSort(self.liststore)

        self.modelsort.set_sort_column_id(3, Gtk.SortType.DESCENDING)
        self.set_model(self.modelsort)

        self.get_selection().set_mode(Gtk.SelectionMode.BROWSE)
        self.set_headers_visible(True)

        column = Gtk.TreeViewColumn(_("Move"), Gtk.CellRendererText(), text=1)
        column.set_sort_column_id(1)
        column.connect("clicked", self.column_clicked, 1)
        self.append_column(column)

        column = Gtk.TreeViewColumn(_("Score"), Gtk.CellRendererProgress(), value=2)
        column.set_min_width(80)
        column.set_sort_column_id(2)
        column.connect("clicked", self.column_clicked, 2)
        self.append_column(column)

        column = Gtk.TreeViewColumn(_("Count"), Gtk.CellRendererText(), text=3)
        column.set_sort_column_id(3)
        column.connect("clicked", self.column_clicked, 3)
        self.append_column(column)

        self.cid = None
        selection = self.get_selection()
        self.cid = selection.connect_after("changed", self.row_changed)

        self.board = LBoard()
        self.board.applyFen(FEN_START)
        self.update_tree(self.get_openings(0, self.board))

        # self.set_cursor(0)
        self.columns_autosize()

        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.add(self)

        self.box.pack_start(sw, True, True, 0)
        self.box.show_all()

    def column_clicked(self, col, data):
        # print("column_clicked")
        self.set_search_column(data)

    def row_changed(self, selection):
        # print("row_changed")
        model, iter = selection.get_selected()
        if iter is not None:
            lmove = self.liststore[self.modelsort.convert_iter_to_child_iter(iter)][0]
            # print("move %s selected" % lmove)
            self.board.applyMove(lmove)
            self.update_tree(self.get_openings(0, self.board))

    def get_openings(self, ply, board):
        print("get_openings()")
        # print(board)
        result = []
        bb = board.friends[0] | board.friends[1]
        bb_list = self.gamelist.chessfile.get_bitboards(board.plyCount + 1)
        print("got %s bitboards" % len(bb_list))
        for lmove in genAllMoves(board):
            board.applyMove(lmove)
            for bb, count in bb_list:
                if bb + 2**63 - 1 == board.friends[0] | board.friends[1]:
                    result.append((lmove, count))
                    break
            board.popMove()
        print("got %s moves" % len(result))
        return result

    def update_tree(self, openings):
        # print("update_tree")
        if self.cid is not None:
            with GObject.signal_handler_block(self.get_selection(), self.cid):
                self.liststore.clear()
        else:
            self.liststore.clear()

        for lmove, count in openings:
            self.liststore.append([lmove, toSAN(self.board, lmove), 45, count])