# ライブラリのインポート
import csv
import os
import subprocess
import sys
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

import jaconv
import regex
import spacy
import sudachipy
import sudachidict_core
from tkinterdnd2 import *


class Application:
    def __init__(self):
        # ルビ
        self.RubyMae = ["|", "[[rb:", "<ruby>"]
        self.RubyNaka = ["《", ">", "<rt>"]
        self.RubyUsiro = ["》", "]]", "</rt></ruby>"]

        self.root = TkinterDnD.Tk()
        # self.root.title("ルビ振りくん（体験版）") #体験版
        self.root.title("ルビ振りくん")

        if getattr(sys, "frozen", False):
            self.datadir = os.path.dirname(sys.executable)
        else:
            self.datadir = os.path.dirname(__file__)

        # self.icon_path = os.path.join(self.datadir,"_internal","icon5.ico") #exe時
        self.icon_path = os.path.join(self.datadir, "icon5.ico")  # vscode時
        self.root.iconbitmap(default=self.icon_path)

        self.SyuturyokuFolder = os.path.join(self.datadir, "出力フォルダ")
        self.CreateFolder()

        self.path_jisyo = os.path.join(self.SyuturyokuFolder, "ユーザー辞書.csv")

        self.Lframe1 = ttk.Labelframe(
            self.root, text="ここに.txtファイルをドラッグ&ドロップ", labelanchor="s"
        )
        self.Lframe1.drop_target_register(DND_FILES)
        self.Lframe1.dnd_bind("<<Drop>>", self.drop)
        self.dndtext = tk.StringVar()
        self.dndtext.set("ファイル名")
        self.label1 = ttk.Label(self.Lframe1, textvariable=self.dndtext)
        self.dndtext2 = tk.StringVar()
        self.dndtext2.set("\nここにファイルをD&D")
        self.label2 = ttk.Label(self.Lframe1, textvariable=self.dndtext2)
        self.progbar = ttk.Progressbar(
            self.Lframe1, length=150, mode="determinate", maximum=1
        )
        self.label1.pack(padx=5, pady=5)
        self.label2.pack(padx=5, pady=5)
        self.progbar.pack(padx=5, pady=5)
        self.Lframe1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.RubySentaku = tk.IntVar()
        self.RubySentaku.set(0)
        self.labelFrame2_1 = ttk.Labelframe(
            self.root, text="出力するルビ記法の選択", labelanchor="s", padding=10
        )
        self.rb1 = ttk.Radiobutton(
            self.labelFrame2_1,
            text="小説家になろう、カクヨム\nハーメルン、note、青空文庫など",
            value=0,
            variable=self.RubySentaku,
        )
        self.rb2 = ttk.Radiobutton(
            self.labelFrame2_1, text="pixiv", value=1, variable=self.RubySentaku
        )
        self.rb3 = ttk.Radiobutton(
            self.labelFrame2_1, text="HTML", value=2, variable=self.RubySentaku
        )
        self.labelFrame2_1.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.rb1.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.rb2.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.rb3.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.Lframe2 = ttk.Labelframe(self.root, text="ルビを振る", labelanchor="nw")
        self.button2_1 = ttk.Button(
            self.Lframe2,
            text="全てにルビ振り",
            command=self.RubySubeteFuriFun,
            state="disable",
            padding=3,
        )
        self.button2_2 = ttk.Button(
            self.Lframe2,
            text="辞書のルビ振り",
            command=self.RubyUserFun,
            state="disable",
            padding=3,
        )
        self.button2_3 = ttk.Button(
            self.Lframe2, text="ユーザー辞書", command=self.Jisyo, padding=3
        )
        self.button2_1.grid(row=0, column=0, padx=2, pady=5, sticky="ew")
        self.button2_2.grid(row=0, column=1, padx=2, pady=5, sticky="ew")
        self.button2_3.grid(row=0, column=2, padx=2, pady=5, sticky="ew")
        self.Lframe2.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.Lframe3 = ttk.Labelframe(self.root, text="その他の機能", labelanchor="nw")
        self.button3_1 = ttk.Button(
            self.Lframe3,
            text="ルビ変換",
            command=self.RubyHenkan,
            state="disable",
            padding=3,
        )
        self.button3_2 = ttk.Button(
            self.Lframe3,
            text="表示確認",
            command=self.HyoujiKakunin,
            state="disable",
            padding=3,
        )
        self.button3_3 = ttk.Button(
            self.Lframe3,
            text="一行開けをする",
            command=self.KaigyouFun,
            state="disable",
            padding=3,
        )
        self.button3_4 = ttk.Button(
            self.Lframe3, text="フォルダを開く", command=self.OpenFolder, padding=3
        )
        self.button3_1.grid(row=0, column=0, padx=2, pady=5, sticky="ew")
        self.button3_2.grid(row=0, column=1, padx=2, pady=5, sticky="ew")
        self.button3_3.grid(row=0, column=2, padx=2, pady=5, sticky="ew")
        self.button3_4.grid(row=1, column=2, padx=2, pady=5, sticky="ew")
        self.Lframe3.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        # 体験版
        # self.label4_1 = ttk.Label(
        #    self.root,
        #    text="このソフトは体験版です\nルビ振り・変換機能は200文字までしか読み込みません",
        #    anchor="center",
        # )
        # self.label4_1.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)
        # self.root.rowconfigure(4, weight=1)  # 体験版

        self.labelFrame2_1.columnconfigure(0, weight=1)
        self.labelFrame2_1.columnconfigure(1, weight=1)
        self.labelFrame2_1.columnconfigure(2, weight=1)
        self.labelFrame2_1.rowconfigure(0, weight=1)

        self.Lframe2.columnconfigure(0, weight=1)
        self.Lframe2.columnconfigure(1, weight=1)
        self.Lframe2.columnconfigure(2, weight=1)
        self.Lframe2.rowconfigure(0, weight=1)

        self.Lframe3.columnconfigure(0, weight=1)
        self.Lframe3.columnconfigure(1, weight=1)
        self.Lframe3.columnconfigure(2, weight=1)
        self.Lframe3.rowconfigure(0, weight=1)
        self.Lframe3.rowconfigure(1, weight=1)

        self.nlp = spacy.load("ja_ginza")

        self.p = regex.compile(r"\p{Script=Han}+")

        self.sub_win = None
        self.SyuturyokuSaigo = ""

        # 動作開始
        self.root.mainloop()

    def drop(self, event):  # ファイルをD&Dした時の処理
        self.Pathname = event.data
        self.pathslice0 = self.Pathname[:1]
        self.pathslice1 = self.Pathname[-1:]
        if self.pathslice0 == "{" and self.pathslice1 == "}":
            self.Pathname = self.Pathname[1:-1]
        self.filename = os.path.basename(self.Pathname)
        self.dndtext.set(self.filename)
        self.filename2 = os.path.splitext(os.path.basename(self.Pathname))[0]
        with open(self.Pathname, mode="r", encoding="UTF-8") as f:
            self.HonbunText = f.read()

        # self.HonbunText = self.HonbunText[:200]  # 体験版

        self.button2_1["state"] = "disable"
        self.button2_2["state"] = "disable"
        self.button3_3["state"] = "disable"
        self.button3_1["state"] = "disable"
        self.button3_2["state"] = "disable"

        self.RubyHantei()
        self.button2_1["state"] = "normal"
        self.button2_2["state"] = "normal"
        self.button3_3["state"] = "normal"
        self.Kokuti = "ルビが振られて「いない」ファイルです"
        self.dndtext2.set(self.Kokuti + "\n機能が一部制限されます")
        if not self.HenkanMoto == 3:
            self.button3_1["state"] = "normal"
            self.button3_2["state"] = "normal"
            self.Kokuti = "ルビが振られて「いる」ファイルです"
            if self.HenkanMoto == 0:
                self.Kokutiruby = "\n小説家になろうなどの記法です"
            elif self.HenkanMoto == 1:
                self.Kokutiruby = "\npixivの記法です"
            elif self.HenkanMoto == 2:
                self.Kokutiruby = "\nHTMLの記法です"
            self.dndtext2.set(self.Kokuti + self.Kokutiruby)

    def RubyHantei(self):  # D&Dされたファイルにルビが振られているか
        if (
            "|" in self.HonbunText
            and "《" in self.HonbunText
            and "》" in self.HonbunText
        ):
            self.HenkanMoto = 0
        elif (
            "[[rb:" in self.HonbunText
            and ">" in self.HonbunText
            and "]]" in self.HonbunText
        ):
            self.HenkanMoto = 1
        elif (
            "<ruby>" in self.HonbunText
            and "<rt>" in self.HonbunText
            and "</rt></ruby>" in self.HonbunText
        ):
            self.HenkanMoto = 2
        else:
            self.HenkanMoto = 3

    def RubySubeteFuriFun(self):  # 総ルビのボタンを押されたら
        self.SyoriHonbun = ""
        self.SyoriHonbun = self.HonbunText
        if not self.HenkanMoto == 3:
            self.re_message = messagebox.askokcancel(
                title="情報提供",
                message="既にルビが振られています\nルビを振ってもいいですか？",
            )
        else:
            self.re_message = True
        if self.re_message == True:
            self.SentakuKihou()
            self.TSentaku = self.Sentaku
            self.Sentaku = 0
            if self.HenkanMoto == 1 or self.HenkanMoto == 2:
                self.Henakan()  # 他のルビ記法の場合なろう記法へ
                if self.HenkanMoto == 2:
                    self.HTML2Hutsu()
            self.RubyUser()  # ユーザー辞書のやつ変換
            self.RubyFuri()  # 全体を変換
            self.Thenkan = self.HenkanMoto
            self.HenkanMoto = 0
            self.Sentaku = self.TSentaku
            if not self.Sentaku == 0:
                self.Henakan()
            if self.Sentaku == 2:
                self.Hutsu2HTML()
            self.KanseiHonbun = self.SyoriHonbun
            self.SyuturyokuSaigo = "_ルビ振り済み（総ルビ）.txt"
            self.KanseiKakikomi()
            self.HenkanMoto = self.Thenkan
            self.dndtext2.set(self.Kokuti + "\nルビ振り完了（総ルビ）")
            self.OpenFolder()

    def RubyUserFun(self):  # 辞書ルビ振りのボタンを押されたら
        if os.path.isfile(self.path_jisyo):
            self.SyoriHonbun = ""
            self.SyoriHonbun = self.HonbunText
            self.SentakuKihou()
            self.RubyUser()
            self.KanseiHonbun = self.SyoriHonbun
            self.SyuturyokuSaigo = "_ルビ振り済み（辞書）.txt"
            self.KanseiKakikomi()
            self.dndtext2.set(self.Kokuti + "\nルビ振り完了（辞書）")
            self.OpenFolder()
        else:
            messagebox.showerror(
                title="エラー",
                message="ユーザー辞書が存在しません\nルビを登録してください",
            )

    def RubyUser(self):  # ユーザー辞書に登録された文字にルビを振る。置換。
        self.UserJisyoYomikomi()
        self.User_list = []
        for self.UTango in self.Userjisyo:
            self.UHbun = (
                self.RubyMae[self.Sentaku]
                + self.UTango[0]
                + self.RubyNaka[self.Sentaku]
                + self.UTango[1]
                + self.RubyUsiro[self.Sentaku]
            )
            self.SyoriHonbun = self.SyoriHonbun.replace(self.UHbun, self.UTango[0])
            self.SyoriHonbun = self.SyoriHonbun.replace(self.UTango[0], self.UHbun)

    def SentakuKihou(self):
        self.Sentaku = self.RubySentaku.get()

    def KanseiKakikomi(self):
        self.CreateFolder()
        self.path_Ruby = os.path.join(
            self.SyuturyokuFolder, self.filename2 + self.SyuturyokuSaigo
        )
        with open(self.path_Ruby, mode="w", encoding="UTF-8") as fw:
            fw.write(self.KanseiHonbun)

    def UserJisyoYomikomi(self):
        self.Userjisyo = []
        if os.path.isfile(self.path_jisyo):
            with open(self.path_jisyo, mode="r", encoding="shift-jis") as f:
                self.reader = csv.reader(f)
                self.Userjisyo = [self.row for self.row in self.reader]

    def Jisyo(self):
        if self.sub_win == None or not self.sub_win.winfo_exists():
            self.UserJisyoYomikomi()
            self.list_items = []
            for self.lrow in self.Userjisyo:
                self.list_items.append(self.lrow[0] + "：" + self.lrow[1])
            self.List_var = tk.StringVar(value=self.list_items)

            self.sub_win = tk.Toplevel()
            self.sub_win.title("ユーザー辞書")
            self.label5_1 = ttk.Label(
                self.sub_win, text="ユーザー辞書への登録", anchor="center"
            )

            self.Lframe5_1 = ttk.Labelframe(
                self.sub_win, text="登録済みのルビ", labelanchor="nw"
            )
            self.frame5_2 = ttk.Frame(self.Lframe5_1)
            self.ListBox = tk.Listbox(self.frame5_2, listvariable=self.List_var)
            self.List_width_check()
            self.scrollbar = ttk.Scrollbar(
                self.frame5_2, orient="vertical", command=self.ListBox.yview
            )
            self.ListBox["yscrollcommand"] = self.scrollbar.set
            self.button5_1 = ttk.Button(
                self.Lframe5_1, text="削除", command=self.Jisyosakujyo, padding=3
            )

            self.Lframe5_3 = ttk.Labelframe(
                self.sub_win, text="新規登録", labelanchor="nw"
            )
            self.label5_2 = ttk.Label(
                self.Lframe5_3, text="ルビを振る文字", anchor="center"
            )
            self.label5_3 = ttk.Label(self.Lframe5_3, text="ルビ", anchor="center")
            self.entry_1 = ttk.Entry(self.Lframe5_3)
            self.entry_2 = ttk.Entry(self.Lframe5_3)
            self.button5_2 = ttk.Button(
                self.Lframe5_3, text="登録", command=self.JisyoTouroku, padding=3
            )

            self.label5_1.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

            self.Lframe5_1.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
            self.frame5_2.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            self.ListBox.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            self.scrollbar.grid(row=0, column=1, sticky="ns")
            self.button5_1.grid(row=1, column=0, padx=5, pady=5, sticky="e")

            self.Lframe5_3.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
            self.label5_2.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            self.label5_3.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.entry_1.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
            self.entry_2.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            self.button5_2.grid(row=2, column=1, padx=5, pady=5, sticky="e")

            self.sub_win.columnconfigure(0, weight=1)
            self.sub_win.rowconfigure(0, weight=1)
            self.sub_win.rowconfigure(1, weight=1)
            self.sub_win.rowconfigure(2, weight=1)

            self.Lframe5_1.columnconfigure(0, weight=1)
            self.Lframe5_1.rowconfigure(0, weight=1)
            self.Lframe5_1.rowconfigure(1, weight=1)

            self.frame5_2.columnconfigure(0, weight=1)
            self.frame5_2.rowconfigure(0, weight=1)

            self.Lframe5_3.columnconfigure(0, weight=1)
            self.Lframe5_3.columnconfigure(1, weight=1)
            self.Lframe5_3.rowconfigure(0, weight=1)
            self.Lframe5_3.rowconfigure(1, weight=1)
            self.Lframe5_3.rowconfigure(2, weight=1)

    def List_width_check(self):
        self.saidaimoji = 0
        for self.row in self.list_items:
            if self.saidaimoji <= len(self.row):
                self.saidaimoji = len(self.row)
        self.List_width = self.saidaimoji * 2
        if self.List_width <= 40:
            self.List_width = 40
        self.ListBox["width"] = self.List_width

    def Jisyosakujyo(self):
        self.select = self.ListBox.curselection()
        self.ListBox.delete(self.select)
        del self.list_items[self.select[0]]
        del self.Userjisyo[self.select[0]]
        self.List_var.set(self.list_items)
        self.JisyoKakikomi()
        self.List_width_check()

    def JisyoTouroku(self):
        self.Nyuryoku1 = self.entry_1.get()
        self.Nyuryoku2 = self.entry_2.get()
        if self.Nyuryoku1 == "" or self.Nyuryoku2 == "":
            messagebox.showerror(title="エラー", message="両方に文字を入れてください")
            self.sub_win.lift()
        else:
            self.Userjisyo.append([self.Nyuryoku1, self.Nyuryoku2])
            self.list_items.append(self.Nyuryoku1 + "：" + self.Nyuryoku2)
            self.List_var.set(self.list_items)
            self.entry_1.delete(0, tk.END)
            self.entry_2.delete(0, tk.END)
            self.JisyoKakikomi()
            self.List_width_check()

    def JisyoKakikomi(self):
        self.CreateFolder()
        with open(self.path_jisyo, mode="w", newline="", encoding="shift-jis") as f:
            self.writer = csv.writer(f)
            self.writer.writerows(self.Userjisyo)

    def RubyFuri(self):
        self.SyoriList = []
        self.Tcheck = 0
        self.TyuukanHonbun = self.SyoriHonbun.split("\n")
        for i, item in enumerate(self.TyuukanHonbun, 1):
            self.SyoriSouHonbun = ""
            self.doc = self.nlp(item)
            for self.sent in self.doc.sents:
                for self.token in self.sent:
                    self.Motomoji = self.token.orth_
                    if self.Motomoji == "|":
                        self.Tcheck = 1
                        self.TashiTan = self.Motomoji
                    elif self.Motomoji == "《" and self.Tcheck == 1:
                        self.Tcheck = 2
                        self.TashiTan = self.Motomoji
                    elif self.Motomoji == "》" and self.Tcheck == 2:
                        self.Tcheck = 0
                        self.TashiTan = self.Motomoji
                    elif not self.token.tag_ == "空白":
                        self.Yomimoji = jaconv.kata2hira(
                            self.token.morph.get("Reading")[0]
                        )
                        kanji = ""
                        tyuukan = ""
                        yomi1 = self.Yomimoji
                        # ルビを振る文字列から1個ずつ取り出す
                        for j in range(len(self.Motomoji)):
                            char = self.Motomoji[j]
                            # 漢字かをチェック
                            if self.p.fullmatch(char):
                                kanji += char
                            else:
                                # 漢字が溜まっているか
                                if kanji == "":
                                    tyuukan += char
                                    yomi1 = yomi1[1:]
                                else:
                                    mae = yomi1.find(jaconv.kata2hira(char))
                                    rubi = yomi1[:mae]
                                    rubihuri = "|" + kanji + "《" + rubi + "》"
                                    tyuukan += rubihuri
                                    tyuukan += char
                                    kanji = ""
                                    yomi1 = yomi1[mae + 1 :]
                        if not kanji == "":
                            rubi = yomi1
                            rubihuri = "|" + kanji + "《" + rubi + "》"
                            tyuukan += rubihuri

                        # ルビが振られていない場合
                        if "《》" in tyuukan:
                            yomi2 = self.Yomimoji
                            tyuukan = ""
                            kanji = ""
                            for k in range(len(self.Motomoji) - 1, -1, -1):
                                char = self.Motomoji[k]
                                if self.p.fullmatch(char):
                                    kanji = char + kanji
                                else:
                                    # 漢字が溜まっているか
                                    if kanji == "":
                                        tyuukan = char + tyuukan
                                        yomi2 = yomi2[:-1]

                                    else:
                                        mae = yomi2.rfind(jaconv.kata2hira(char))
                                        rubi = yomi2[mae + 1 :]
                                        rubihuri = "|" + kanji + "《" + rubi + "》"
                                        tyuukan = rubihuri + tyuukan
                                        tyuukan = char + tyuukan
                                        kanji = ""
                                        yomi2 = yomi2[:mae]
                            if not kanji == "":
                                rubi = yomi2
                                rubihuri = "|" + kanji + "《" + rubi + "》"
                                tyuukan = rubihuri + tyuukan
                        self.TashiTan = tyuukan
                    else:
                        self.TashiTan = self.Motomoji
                    self.SyoriSouHonbun += self.TashiTan
            self.SyoriList.append(self.SyoriSouHonbun)
            self.progbar.configure(value=(i) / len(self.TyuukanHonbun))
            self.progbar.update()
        self.SyoriHonbun = "\n".join(self.SyoriList)

    def CreateFolder(self):
        os.makedirs(self.SyuturyokuFolder, exist_ok=True)

    def OpenFolder(self):
        self.CreateFolder()
        subprocess.Popen(["explorer", self.SyuturyokuFolder], shell=True)

    def RubyHenkan(self):  # 変換ボタンを押されたら
        self.SyoriHonbun = ""
        self.SyoriHonbun = self.HonbunText
        self.SentakuKihou()
        self.Henakan()
        if self.HenkanMoto == 2 and not self.Sentaku == 2:
            self.HTML2Hutsu()
        if not self.HenkanMoto == 2 and self.Sentaku == 2:
            self.Hutsu2HTML()
        self.KanseiHonbun = self.SyoriHonbun
        self.CreateFolder()
        self.SyuturyokuSaigo = "_変換済み.txt"
        self.KanseiKakikomi()
        self.dndtext2.set(self.Kokuti + "\nルビ変換完了")
        self.OpenFolder()

    def Henakan(self):
        self.SyoriHonbun = self.SyoriHonbun.replace(
            self.RubyNaka[self.HenkanMoto], self.RubyNaka[self.Sentaku]
        )
        self.SyoriHonbun = self.SyoriHonbun.replace(
            self.RubyMae[self.HenkanMoto], self.RubyMae[self.Sentaku]
        )
        self.SyoriHonbun = self.SyoriHonbun.replace(
            self.RubyUsiro[self.HenkanMoto], self.RubyUsiro[self.Sentaku]
        )

    def Hutsu2HTML(self):
        self.SyoriHonbun = self.SyoriHonbun.replace("\n", "<br>\n")
        self.SyoriHonbun = self.SyoriHonbun.replace(" ", "&nbsp;")
        self.SyoriHonbun = self.SyoriHonbun.replace("　", "&emsp;")

    def HTML2Hutsu(self):
        self.SyoriHonbun = self.SyoriHonbun.replace("<br>\n", "\n")
        self.SyoriHonbun = self.SyoriHonbun.replace("&nbsp;", " ")
        self.SyoriHonbun = self.SyoriHonbun.replace("&emsp;", "　")

    def HyoujiKakunin(self):  # 表示確認ボタンを押された時
        self.SyoriHonbun = ""
        self.SyoriHonbun = self.HonbunText
        self.HTMLMae = "<!doctype html><head><title>ルビの表示確認</title><body><p>"
        self.HTMLUshiro = "</p></body></html>"
        if self.HenkanMoto == 3:
            messagebox.showinfo(title="情報提供", message="ルビが振られていません")
        else:
            self.RubySentaku.set(2)
            self.SentakuKihou()
            self.Henakan()
            self.Hutsu2HTML()
            self.KanseiHonbun = self.HTMLMae + self.SyoriHonbun + self.HTMLUshiro
            self.CreateFolder()
            self.path_Ruby = os.path.join(self.SyuturyokuFolder, "ルビ確認用.html")
            with open(self.path_Ruby, mode="w", encoding="UTF-8") as fw:
                fw.write(self.KanseiHonbun)
            webbrowser.open_new_tab(self.path_Ruby)

    def KaigyouFun(self):  # 改行を入れるボタンを押されたら
        self.SyoriHonbun = ""
        self.SyoriHonbun = self.HonbunText
        if self.HenkanMoto == 2:
            self.SyoriHonbun = self.SyoriHonbun.replace("<br>", "<br><br>")
        else:
            self.SyoriHonbun = self.SyoriHonbun.replace("\n", "\n\n")
        self.KanseiHonbun = self.SyoriHonbun
        self.SyuturyokuSaigo = "_改行済み.txt"
        self.KanseiKakikomi()
        self.dndtext2.set(self.Kokuti + "\n改行完了")
        self.OpenFolder()


Application()
