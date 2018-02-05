from ttk import *

class ListView(Treeview):
    def initColumn(self,cols):
        #self["show"] = "headings"
        self["height"] = 10
        keys = []
        self.cols = {}
        self.rows={}
        for i,col in enumerate(cols):
            keys.append(col["key"])
        self["columns"] = tuple(keys)
        for i,col in enumerate(cols):
            self.column(col["key"],width=col["width"])
            self.heading(col["key"],text=col["text"])
            col["index"] = i
            self.cols[col["key"]] = col

    def insertRow(self,row):
        identifyKey = row[row["identifyKey"]]
        if self.rows.has_key(identifyKey) :
            for key,col in self.cols.items():
                value = row[key]
                self.setData(identifyKey,key,value)
                return
        values = []
        for key,col in self.cols.items():
            if row.has_key(key) :
                value = row[key]
                values.insert(col["index"],value)
            else:
                values.insert(col["index"],'')
        rowKey = self.insert("","end",values=tuple(values))
        rowData = {}
        rowData["key"] = rowKey
        rowData["data"] = values
        self.rows[identifyKey] = rowData

    def insertChildRow(self,parentKey,row):
        if self.rows.has_key(parentKey):
            rd = self.rows[parentKey]
            parentItemKey = rd['key']
            values = []
            for key,col in self.cols.items():
                if row.has_key(key) :
                    value = row[key]
                    values.insert(col["index"],value)
                else:
                    values.insert(col["index"],'')
            identifyKey = parentKey + "_" + row[row["identifyKey"]]
            rowKey = self.insert(parentItemKey,"end",values=tuple(values))
            rowData = {}
            rowData["key"] = rowKey
            rowData["data"] = values
            self.rows[identifyKey] = rowData

    def setData(self,identifyKey,colKey,value):
        if self.rows.has_key(identifyKey) :
            rowData = self.rows[identifyKey]
            rowKey = rowData["key"]
            values = rowData["data"]
            col = self.cols[colKey]
            values[col["index"]] = value
            self.set(rowKey,colKey,value)