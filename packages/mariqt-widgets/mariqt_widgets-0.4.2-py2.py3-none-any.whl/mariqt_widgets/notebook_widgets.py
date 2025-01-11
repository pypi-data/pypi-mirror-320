import datetime
import ipywidgets as widgets
try:
    from ipyfilechooser import FileChooser
except ModuleNotFoundError as er:
    raise ModuleNotFoundError(str(er.args) + "\n Install with e.g. $ pip install ipyfilechooser")
import markdown
import sys
import os
from io import StringIO
import functools
import difflib
import abc
import inspect
import copy
import html
from IPython.display import display
import traitlets

import mariqt.variables as miqtv
import mariqt.converters as miqtconv

myPath = os.path.dirname(__file__)
ICON_CHECK = open(myPath + "/icons/checkbox-circle-line_green.png", "rb").read()
ICON_CHECKDISABLED = open(myPath + "/icons/checkbox-circle-line_gray.png", "rb").read()
ICON_ERROR = open(myPath + "/icons/error-warning-line_red.png", "rb").read()
ICON_ERRORDISABLED = open(myPath + "/icons/error-warning-line_gray.png", "rb").read()
ICON_WARNING = open(myPath + "/icons/error-warning-line_orange.png", "rb").read()


class MarkdownWidget(widgets.HTML):

    def __init__(self, value=None):
        if not value is None:
            value = markdown.markdown(value)
        widgets.HTML.__init__(self,value=value)


class MyLabel(widgets.HTML):
    """ Label that allows disabling as well as markdown notation. Use 'myvalue' instead of value """

    def __init__(self,value=""):
        """ Label that allows disabling as well as markdown notation. Use 'myvalue' instead of value """
        widgets.HTML.__init__(self)
        self._myvalue = value
        self.disabled = False
        self.paint()
        
    def paint(self):
        txt = markdown.markdown(self.myvalue)
        if not self.disabled:
            self.value = f"<p><font color='black'>{txt}</p>"
        else:
            self.value = f"<p><font color='grey'>{txt}</p>"

    @property
    def disabled(self):
        return self._disabled 

    @disabled.setter
    def disabled(self, value):
        self._disabled = value
        self.paint()
            
    @property
    def myvalue(self):
        return self._myvalue 

    @myvalue.setter
    def myvalue(self, value):
        self._myvalue = value
        self.paint()


class MyScrollbox(widgets.HBox):
    """ Creates a scrollable text area that is not editable with fixed size """
    def __init__(self,value,height='60px'):
        testColor='#808080'
        borderColor='#C0C0C0'
        text = html.escape(value).replace("\n","<br/>").replace("\t", "&nbsp;&nbsp;&nbsp;")
        htmlw = widgets.HTML(
            value= f"<p style=line-height:150%><font color={testColor}>{text}</p>",
            disabled=True,
            color='#d5d8dc',
            layout=widgets.Layout(lineheight='80%'),
            width='auto'
        )
        widgets.HBox.__init__(self,[htmlw], layout=widgets.Layout(width='auto',
                                                         height=height,
                                                         overflow_y='auto',
                                                         border='solid 1px '+borderColor,
                                                         padding='0px 8px 0px 8px',
                                                         margin='2px 0px 2px 0px'))

def escapeHTML(msg:str):
    return formatHTML(html.escape(msg).replace("\n","<br/>").replace("\t", "&nbsp;&nbsp;&nbsp;"))
def formatHTML(msg:str):
    return f"<p style=\"font-family:monospace;\">{msg}</p>"

class MyHtmlWidget(widgets.HTML):
    """ text widget to avoid creation of scroll box in jupyter notebook due to output size change. """
    def __init__(self):
        widgets.HTML.__init__(self)
        self.text = "" 

    def addText(self,text:str):
        if text != "" and text != "[]":
            self.text += "\n" + text
            self.value = escapeHTML(self.text)


class MyValid(widgets.VBox):
    """ Valid that has no aligment bug and allows disabling """
    def __init__(self,valid=True,disabled = False,margin_top:float=7):
        
        self.image = widgets.Image()
        
        widgets.VBox.__init__(self,[self.image],layout=widgets.Layout(margin=str(margin_top) + 'px 0 0 0px'))

        self.icon_check = ICON_CHECK
        self.icon_checkDisabled = ICON_CHECKDISABLED
        self.icon_error = ICON_ERROR
        self.icon_errorDisabled = ICON_ERRORDISABLED
        self.icon_warning = ICON_WARNING
        self._valid = valid
        self._disabled = disabled
        self._warning = False
        self.image.layout.width = '15px'
        self.image.layout.hight = '15px'
        self.image.layout.max_width = '15px'
        self.image.layout.max_hight = '15px'
        
        self.paint()
        
    def warningOnce(self):
        """ sets next invalid to warning """
        self.warning = True

    def paint(self):
        if self.valid:
            if self.disabled:
                if self.warning:
                    self.image.value = self.icon_errorDisabled
                else:
                    self.image.value = self.icon_checkDisabled
            else:
                if self.warning:
                    self.image.value = self.icon_warning
                else:
                    self.image.value = self.icon_check
        else:
            if self.disabled:
                self.image.value = self.icon_errorDisabled
            else:
                self.image.value = self.icon_error
            # else:
            #     if self.warning:
            #         self.value = self.icon_warning
            #         self.warning = False
            #     else:
            #         self.value = self.icon_error

    @property
    def valid(self):
        return self._valid

    @valid.setter
    def valid(self, value):
        self._valid = value
        if self._valid:
            self._warning = False
        self.paint()

    @property
    def warning(self):
        return self._warning

    @warning.setter
    def warning(self, value):
        self._warning = value
        if self._warning:
            self._valid = True
        self.paint()
            
    @property
    def disabled(self):
        return self._disabled 

    @disabled.setter
    def disabled(self, value):
        self._disabled = value
        self.paint()


class FileChooserPaste(FileChooser):
    def __init__(self, path: str = '', filename: str = '', title: str = '', select_desc: str = 'Select', change_desc: str = 'Change', show_hidden: bool = False, select_default: bool = False, dir_icon = '\U0001F4C1 ', dir_icon_append: bool = False, show_only_dirs: bool = False, filter_pattern = None, sandbox_path = None, **kwargs):
        """ File Chooser that also has field to paste a file path. Get Full widget with .getWidget() """
        super().__init__(path, filename, title, select_desc, change_desc, show_hidden, select_default, dir_icon, dir_icon_append, show_only_dirs, filter_pattern, sandbox_path, **kwargs)

        self.filePathWidget = widgets.Text(layout=widgets.Layout(width='50px'))
        self.filePathWidget.observe(self._filePathWidget_changed)
        self.skip_filePathWidget_changed = False
        margin = '2px'
        padding = '4px'
        self.myWidget = widgets.VBox([self,widgets.HBox([widgets.Label('or paste here:'),self.filePathWidget])],
                                        layout={'border': '1px solid #C0C0C0','margin': " ".join(4*[margin]),'padding': " ".join(4*[padding])})

    def getWidget(self):
        return self.myWidget

    def _on_file_selected(self,b):
        if self.selected == None:
            self.filePathWidget.value = ""
        else:
            self.filePathWidget.value = self.selected

    def _filePathWidget_changed(self,foo):
        if foo['name'] == 'value':
            new = foo['new']
            old = foo['old']
            if self.skip_filePathWidget_changed == True:
                self.skip_filePathWidget_changed = False
                return

            valid = os.path.isfile(new)
            if self.show_only_dirs == True:
                valid = os.path.exists(new)
                # dir path must end with / otherwise the function is called a second time with the last part removed
                if valid and new[-1] != "/":
                    new += "/"
                    self.filePathWidget.value = new
                    return
            if valid:
                path = str(os.path.dirname(new))
                filename = ""
                if self.show_only_dirs == False:
                    filename = str(os.path.basename(new))
                self._set_form_values(path, filename)
                self._apply_selection()
                self._on_file_selected(0)
                # Execute callback function
                if self._callback is not None:
                    try:
                        self._callback(self)
                    except TypeError:
                        # Support previous behaviour of not passing self
                        self._callback()
            else:
                self.skip_filePathWidget_changed =True
                self.filePathWidget.value = old


class Capturing(list):
    """ caputres output in variable. Use:  with Capturing() as output: """
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout


class VerticalSpacer(widgets.VBox):
    def __init__(self,space:int):
        widgets.VBox.__init__(self,[],layout=widgets.Layout(margin=str(space) + 'px 0 0 0'))


class HorizontalSpacer(widgets.HBox):
    def __init__(self,space:int):
        widgets.HBox.__init__(self,[],layout=widgets.Layout(margin='0 ' + str(space) + 'px  0 0'))




################################ Editable list widget ############################################################

class EditalbleListWidget():
    """ creates a widget containing a list of sub widgets which can be added and removed and are stored in a list """
    def __init__(self,label,itemWidgetExample,iFDOList,repaint_after_delete:bool=True):
        """ label will be displayed above list and in front of "add" button. itemWidgetExample is used to create item by copying it, must be inherited from itemWidgetBase.
        repaint_after_delete: this widget can be used to directly act on iFDOList, i.e. delete an item from it if widget deleted. Alternatively, the list widget
        values can be read afterwards to process the information. In this case the items removeFromSource can be passed and repaint_after_delete needs to be 
        set False """
        

        self._itemWidgetExample = itemWidgetExample
        self.iFDOList = iFDOList # list of respective fields/objs in iFDO 
        self.itemObjList = []    # list of item object
        self.itemsWidget = widgets.VBox([e.widget for e in self.itemObjList]) # list of item objects as widget
        self.repaint_after_delete = repaint_after_delete
        
        # label plus add button
        addButton = widgets.Button(description="+", layout=widgets.Layout(width='auto'))
        addButton.on_click(self.on_addButton_clicked)
        self.labelButtonBox = widgets.HBox([widgets.Label(label), addButton])
        
        # complete widget
        self.completeWidget = widgets.VBox([self.labelButtonBox,self.itemsWidget])
        self.repaint()
    
    def on_addButton_clicked(self,b, params=[]): #fileName="",cols=[]):
        #with Capturing() as output:
        
        #new = FileParserWidget(fileName,cols)

        new = self._itemWidgetExample.copy()

        new.setParams(params)
        newContainer = ItemWidgetContainer(self,new)
        if not newContainer in self.itemObjList:
            self.itemObjList.append(newContainer)
            self.itemsWidget.children += (newContainer.widget,) #[e.widget for e in auxFilesObjs]
            self._itemWidgetExample.on_change_fct(0)
        else:
            newContainer.delete()
        
        #debugOutputWidget.addText(str(output))

    def handleOn_deleteButton_clicked(self,obj):
        #with Capturing() as output:
        
        self.itemObjList.remove(obj)
        self.itemsWidget.children = [e.widget for e in self.itemObjList]
        #iFDO.removeItemInfoTabFile(obj.fileName(),obj.columns())
        self._itemWidgetExample.removeFromSource(obj.itemWidget.getParams())
        obj.widget.close()
        self._itemWidgetExample.on_change_fct(0)
        if self.repaint_after_delete:
            self.repaint()
        #debugOutputWidget.addText(str(output))
            
        obj.delete()

    def repaint(self):
        for item in self.iFDOList:
            tmpNew = self._itemWidgetExample.copy()
            tmpNew.setParams(self._itemWidgetExample.readParamsFromElement(item))
            tmpNewContainer = ItemWidgetContainer(self,tmpNew)
            if not tmpNewContainer in self.itemObjList:
                self.on_addButton_clicked(0,tmpNew.getParams())

    def observe(self, handler, names=traitlets.All, type="change"):
        observe_op = getattr(self._itemWidgetExample, "observe", None)
        if not callable(observe_op):
            return
        else:
            for item in self.itemObjList:
                item.widget.observe(handler, names, type)
                item.itemWidget.observe(handler, names, type)


class ItemWidgetContainer:
    """ contains the item itself plus the delete button """
    def __init__(self,editalbleListWidget,itemWidget):

        self.editalbleListWidget = editalbleListWidget
        self.itemWidget = itemWidget
        deleteButton = widgets.Button(description="Delete")
        deleteButton.on_click(functools.partial(self.on_deleteButton_clicked,obj=self))
        self.widget = widgets.VBox([self.itemWidget.getWidget(),deleteButton,widgets.Label("")])
        
    def on_deleteButton_clicked(self,b,obj):
        #with Capturing() as output:
        self.editalbleListWidget.handleOn_deleteButton_clicked(obj)
        #debugOutputWidget.addText(str(output))

    def delete(self):
        # for FileParserDateTimeWidgetWithMasterTime only
        try:
            self.itemWidget.delete()
        except:
            pass

    def __eq__(self, other):
        if self.itemWidget.getParams() == other.itemWidget.getParams():
            return True
        else:
            return False
            
class ItemWidgetBase:
    """ base class for the list widget that can be used """
    
    def __init__(self,on_change_fct):
        try:
            self.on_change_fct = on_change_fct
            self.on_change_fct(0)
        except Exception:
            def on_change_fct(self,change):
                pass
    
    def __eq__(self, other):
        if self.getParams() == other.getParams():
            return True
        else:
            return False
    
    def copy(self):
        raise NotImplementedError("Please Implement this method")
    
    def setParams(self,params):
        raise NotImplementedError("Please Implement this method")
        
    def getParams(self):
        raise NotImplementedError("Please Implement this method")
        
    def getWidget(self):
        raise NotImplementedError("Please Implement this method")
        
    def removeFromSource(self,params):
        """ what should be done in source if item with params deleted? """
        raise NotImplementedError("Please Implement this method")
        
    def readParamsFromElement(self,element):
        """ how can params be read from the one source element in order to init widget """
        raise NotImplementedError("Please Implement this method")
        
# example
"""
iFDOList = ["value1","value2"]        
class TestWidget(ItemWidgetBase):
    
    def __init__(self,on_change_fct):
        ItemWidgetBase.__init__(self,on_change_fct)
        self.valueWidget = widgets.Text(value="Empty")
        self.widget = widgets.HBox([widgets.Label("Value:"),self.valueWidget])
    
    def copy(self):
        ret = TestWidget(self.on_change_fct)
        ret.setParams(self.getParams())
        return ret
    
    def setParams(self,params=[""]):
        if len(params) == 0:
            params=[""]
        self.valueWidget.value = params[0]
        
    def getParams(self):
        return [self.valueWidget.value]
        
    def getWidget(self):
        return self.widget
    
    def removeFromSource(self,params):
        #print("TODO remove from ifdo:",params)
        if params[0] in iFDOList:
            iFDOList.remove(params[0])
        
    def readParamsFromElement(self,element):
        #print("TODO read params from iFDO element")
        return [element]
    

itemWidgetExample =  TestWidget()
testList = EditalbleListWidget("Name",itemWidgetExample,iFDOList)
#display(testList.completeWidget,output)
"""

#################################################################################################################

################################ FileParserWidget ############################################################

class FileParserWidget(ItemWidgetBase):

    def __init__(self,defaultFields,on_change_fct,requiredFields=[],iFDO=None,ignoreDateTime=True,allowConvert=True,converters:list=[],minFields=1,fixedItemWidthPixels:int=200,allowCustomFields:bool=True,defaultSettings:list=None):
        """
        fixedItemWidthPixels: if None item width is adjusted to space, otherways width is fix and scroll area is created if needed
        """
        ItemWidgetBase.__init__(self,on_change_fct)
        
        self.fixedItemWidthPixels = fixedItemWidthPixels
        self.allowCustomFields = allowCustomFields
        self._defaultSettings = defaultSettings

        self.defaultFields = defaultFields
        self.iFDO = iFDO
        if isinstance(requiredFields,str):
            requiredFields = [requiredFields]
        self.requiredFields = requiredFields
        self._ignoreDateTime = ignoreDateTime
        self._allowConvert = allowConvert
        self._converters = converters
        self._minFields = minFields
        startLocation = ""
        if iFDO is not None:
            startLocation = str(iFDO.getDir().tosensor())

        self.auxFile_file_widget = FileChooserPaste(startLocation) #FileChooser(startLocation)
        self.auxFile_file_widget.register_callback(on_change_fct)
        self.auxFile_file_widget.register_callback(self.on_file_selected)
        self.auxFile_file_widget.register_callback(on_change_fct) # might depend on values set by on_file_selected and vice versa
        
        self.fileValid = MyValid()
        self.on_file_selected(0)

        self.defaultSettingsDropdown = widgets.Dropdown()
        if not self._defaultSettings is None:
            self.defaultSettingsDropdown.options=[("None",["",{}])] + self._defaultSettings
            #self.defaultSettingsDropdown.value=self._defaultSettings[0][1]
            self.defaultSettingsDropdown.layout=widgets.Layout(width='100px')
            self.defaultSettingsDropdown.observe(self.defaultSettingsChanged)

        self.fileSeparator = widgets.Dropdown(options=[('Tab', "\t"), ('Space', " "), (",",","),(";",";")],value="\t",layout=widgets.Layout(width='100px'))
        self.fileSeparator.observe(self.on_file_selected)
        self.fileSeparator.observe(self.on_change_fct)

        addButton = widgets.Button(description="+", layout=widgets.Layout(width='30px'))
        removeButton = widgets.Button(description="-", layout=widgets.Layout(width=addButton.layout.width))

        addButton.on_click(self.on_addButton_clicked)
        removeButton.on_click(self.on_removeButton_clicked)

        self.columnsValid = MyValid()
        if self._allowConvert:
            rowLabels = [widgets.Label("Column Names:"),widgets.Label("Field Names:"),widgets.Label("Converter:")]
        else:
            rowLabels = [widgets.Label("Column Names:"),widgets.Label("Field Names:")]
        auxFile_columsLabel_widget = widgets.HBox([ widgets.VBox(rowLabels),
                                                    widgets.VBox([widgets.HBox([widgets.Label(""),widgets.VBox([self.columnsValid])],layout=widgets.Layout(justify_content='space-between')),widgets.HBox([addButton,removeButton])])],
                                                    layout=widgets.Layout(justify_content='space-between')
                                                    )
        self.columnOptions = []
        if isinstance(self.defaultFields,dict):
            self.fieldNameOptions = [key for key, value in self.defaultFields.items() if '-set-' not in key] # TOOD excluding set should be done here
        else:
            self.fieldNameOptions = self.defaultFields

        columnName = widgets.Dropdown(options=self.columnOptions,layout=widgets.Layout(width='98%'))

        self.auxFile_ColumnsBox_widget = widgets.HBox([]) # needed before definition
        self.requirtedFieldWidgets = []
        for req in requiredFields:
            reqFieldWidget = HeaderFieldWidget(self.columnOptions,self.fieldNameOptions,[self.on_change_fct,self.on_headerFieldWidget_changed],ignoreDateTime=self._ignoreDateTime,allowConvert=self._allowConvert,converters=self._converters, allowCustomFields=self.allowCustomFields)
            
            if self.fixedItemWidthPixels is not None:
                reqFieldWidget.layout.width = str(self.fixedItemWidthPixels)+"px"
            
            reqFieldWidget.comboBox_field.value = req #"image-filename"
            reqFieldWidget.comboBox_field.disabled = True
            self.requirtedFieldWidgets.append(reqFieldWidget)
        
        self.auxFile_ColumnsBox_widget =  widgets.HBox(self.requirtedFieldWidgets,
                                                            layout=widgets.Layout(
                                                            display='flex',
                                                            flex_flow='row',
                                                            width='100%',
                                                            overflow_x='auto',
                                                            flex='1'
                                                            )
                                                            )

        borderColor='#C0C0C0'
        gridBoxItems = [    widgets.HBox([widgets.Label("File:"),widgets.VBox([self.fileValid])],layout=widgets.Layout(justify_content='space-between')),
                            self.auxFile_file_widget.getWidget(),]
        if not self._defaultSettings is None:
            gridBoxItems += [widgets.Label("Default Settings:"),self.defaultSettingsDropdown]
        gridBoxItems += [   widgets.Label("Separator:"),self.fileSeparator,
                            auxFile_columsLabel_widget,widgets.VBox([self.auxFile_ColumnsBox_widget])]
        self.auxFile_widget = widgets.GridBox(gridBoxItems,layout=widgets.Layout(
                                                    border='solid 1px '+borderColor,
                                                    padding='8px 8px 8px 8px',
                                                    margin='2px 0px 2px 2px',
                                                    width='98%',
                                                    grid_template_columns='20% 79%'))

        
        
        self.on_addButton_clicked(0) # have one empty column widget by default

    def defaultSettingsChanged(self,foo):
        if foo['name'] == 'value':
            value = self.defaultSettingsDropdown.value
            try:
                params = [self.auxFile_file_widget.selected] + value
                self.setParams(params)
            except Exception as ex:
                print(ex)


    def on_addButton_clicked(self,b,fieldName="",columnName="",converter={}):

        newHeaderFieldWidget = HeaderFieldWidget(self.columnOptions,self.fieldNameOptions,[self.on_headerFieldWidget_changed,self.on_change_fct],ignoreDateTime=self._ignoreDateTime,allowConvert=self._allowConvert,converters=self._converters, allowCustomFields=self.allowCustomFields)
        
        if self.fixedItemWidthPixels is not None:
            newHeaderFieldWidget.layout.width = str(self.fixedItemWidthPixels)+"px"
        
        if fieldName != "":
            newHeaderFieldWidget.setFieldName(fieldName)
        if columnName != "":
            newHeaderFieldWidget.setColumnName(columnName)
        newHeaderFieldWidget.setCurrentConverter(converter)

        if (fieldName == "" and columnName == "") or newHeaderFieldWidget not in [e for e in self.auxFile_ColumnsBox_widget.children if isinstance(e,HeaderFieldWidget)]:
            if self.fixedItemWidthPixels is not None:
                self.auxFile_ColumnsBox_widget.layout.width = str(self.fixedItemWidthPixels * (len(self.auxFile_ColumnsBox_widget.children)+1) ) + "px"
            self.auxFile_ColumnsBox_widget.children += (newHeaderFieldWidget,)
            self.on_headerFieldWidget_changed(0)
        self.on_change_fct(0)

    def on_removeButton_clicked(self,b):
        if len(self.auxFile_ColumnsBox_widget.children) > self._minFields:
            remove = self.auxFile_ColumnsBox_widget.children[-1]
            self.auxFile_ColumnsBox_widget.children = self.auxFile_ColumnsBox_widget.children[:-1]
            remove.close()
            self.on_headerFieldWidget_changed(0)
            self.on_change_fct(0)
            if self.fixedItemWidthPixels is not None:
                self.auxFile_ColumnsBox_widget.layout.width = str(self.fixedItemWidthPixels * len(self.auxFile_ColumnsBox_widget.children)) + "px"

    def copy(self):
        ret = FileParserWidget(self.defaultFields,self.on_change_fct,self.requiredFields,self.iFDO,ignoreDateTime=self._ignoreDateTime,allowConvert=self._allowConvert,converters=self._converters,fixedItemWidthPixels=self.fixedItemWidthPixels,allowCustomFields=self.allowCustomFields,defaultSettings=self._defaultSettings)
        ret.setParams(self.getParams())
        return ret

    def setParams(self,params=[""]):
        # [filename,separator,headerDict] with headerDict = {<field-name>: {'column-name':value, 'converter':{'name':value,'params':value}}
        #with Capturing() as output:

            if len(params) == 0:
                params = ["","",{}]
            try:
                path = str(os.path.dirname(params[0]))
                filename = str(os.path.basename(params[0]))
            except Exception:
                path = ""
                filename = ""
            if path != "" and filename != "":
                if os.path.exists(params[0]):
                    self.auxFile_file_widget._set_form_values(path, filename)
                    self.auxFile_file_widget._apply_selection()
                    self.on_file_selected(0)
                else:
                    raise Exception("FileParserWidget: file '" + params[0] + "' not found")
            
            if params[1] in [e[1] for e in self.fileSeparator.options]:
                self.fileSeparator.value = params[1]
            elif params[1] != "":
                print(params[1], "not in ", self.fileSeparator.options) # TODO

            self.auxFile_ColumnsBox_widget.children = []
            if params[2] == {}:
                self.on_addButton_clicked(0)
            for field in params[2]:
                self.on_addButton_clicked(0,field,params[2][field]['column-name'],params[2][field]['converter'])
        #debugOutputWidget.addText(str(output))

    def getParams(self):
        # [filename,separator,headerDict] with headerDict = {<field-name>: {'column-name':value, 'converter':{'name':value,'params':value}}
        header = {}
        for item in [widget for widget in self.auxFile_ColumnsBox_widget.children if isinstance(widget,HeaderFieldWidget)]:
            header[item.getFieldName()] = {'column-name':item.getColumnName(), 'converter':item.getCurrentConverter()}
        return [self.auxFile_file_widget.selected,self.fileSeparator.value,header]

    def getWidget(self):
        return self.auxFile_widget

    def removeFromSource(self,params):
        if self.iFDO is None:
            #print("Caution! removeFromSource: iFDO is None")
            return
        self.iFDO.removeItemInfoTabFile(params[0],params[1],params[2])

    def readParamsFromElement(self,element):
        return [element.fileName,element.separator,element.header]

    def on_headerFieldWidget_changed(self,b):
        columnValues = [widget.getColumnName() for widget in self.auxFile_ColumnsBox_widget.children if isinstance(widget,HeaderFieldWidget) and not widget.dropdown_columnName.disabled]
        fieldValues = [widget.getFieldName() for widget in self.auxFile_ColumnsBox_widget.children if isinstance(widget,HeaderFieldWidget)]

        if None in columnValues or "" in columnValues or "" in fieldValues:
            self.columnsValid.valid = False
        elif len(set(columnValues)) != len(columnValues) or len(set(fieldValues)) != len(fieldValues):
            self.columnsValid.warningOnce()
            self.columnsValid.valid = False
        else:
            self.columnsValid.valid = True


    def on_file_selected(self,b):
        if self.auxFile_file_widget.selected == None:
            self.fileValid.valid = False
            return
        try:
            with open(self.auxFile_file_widget.selected,'r') as f:
                self.fileValid.valid = True
                separator = self.fileSeparator.value
                first_line = f.readline().strip()
                fileHeaders = first_line.split(separator)
                self.columnOptions = fileHeaders

                for child in self.auxFile_ColumnsBox_widget.children:
                    if isinstance(child, HeaderFieldWidget):
                        child.setColumnOptions(fileHeaders)
        except (FileNotFoundError, UnicodeDecodeError) as ex:
            self.fileValid.valid = False
            print(ex)
        
        for req in self.requirtedFieldWidgets:
            try:
                req.dropdown_columnName.value = difflib.get_close_matches(req.comboBox_field.value,req.dropdown_columnName.options)[0]
            except IndexError:
                pass

    def valid(self):
        return self.columnsValid.valid == True and self.fileValid.valid == True
                            

class HeaderFieldWidget(widgets.VBox):
    """ VBox widget containing a widget for the header field name and the respective column name in a file to parse from """
    def __init__(self,columnOptions:list,fieldOptions:list,on_change_fct,ignoreDateTime=True,allowConvert=True,converters:list=[],allowCustomFields:bool=True):

        self.allowConvert = allowConvert
        if allowCustomFields:
            self.comboBox_field = widgets.Combobox(options=fieldOptions, placeholder="Field Name",layout=widgets.Layout(width='98%'))
        else:
            self.comboBox_field = widgets.Dropdown(options=fieldOptions, placeholder="Field Name",layout=widgets.Layout(width='98%'))
        self.dropdown_columnName = widgets.Dropdown(options=columnOptions,layout=widgets.Layout(width='98%'))
        self.converterWidgetConainer = widgets.VBox([],layout=widgets.Layout(margin="0px 0px 0px 0px", padding="0px 0px 0px 0px",width='auto',overflow_x='hidden'))

        self.ignoreDateTime = ignoreDateTime
        if not self.ignoreDateTime:
            self.dateTimeFieldKey = "utc datetime"
            self.dateFieldKey = "utc date"
            self.timeFieldKey = "utc time"
            self.dateTimeKeys = [self.dateTimeFieldKey,self.dateFieldKey,self.timeFieldKey]
            for key in self.dateTimeKeys:
                if key not in self.comboBox_field.options:
                    self.comboBox_field.options = list(self.comboBox_field.options) + [key]
            self.comboBox_field.observe(self.on_fieldName_changed)

        self.converterDropdown = widgets.Dropdown(layout=widgets.Layout(width='98%'))
        if converters == []:
            converters= [WidgetNoneConverter()]
        #else:
        #    converters = copy.deepcopy(converters) # otherwise different HeaderFieldWidgets inited with same converters will share same converter instances
        self.availCOnverteroptions = [(e.getName(),copy.copy(e)) for e in converters]
        self.availCOnverteroptions.sort(key=lambda x: len(x[0])) # get None as default
        self.converterDropdown.options = self.availCOnverteroptions
        # bug in windows that value is not set automatically to firt option
        self.converterDropdown.index = 0
        self.converterDropdown.observe(self.on_converter_changed)
        self.on_converter_changed(0)
        if allowConvert:
            self.converterWidgetConainer.children = [self.converterDropdown,self.converterDropdown.value.getWidget()]

        if not isinstance(on_change_fct,list):
            on_change_fct = [on_change_fct]
        for fkt in on_change_fct:
            self.comboBox_field.observe(fkt,names='value')
            self.dropdown_columnName.observe(fkt,names='value')
            self.converterDropdown.observe(fkt)
            
        widgets.VBox.__init__(self,[self.dropdown_columnName,self.comboBox_field,self.converterWidgetConainer],
            layout=widgets.Layout(width='auto',overflow_x='hidden',))

        

    def __eq__(self,other):
        if other.comboBox_field.options == self.comboBox_field.options and \
            other.comboBox_field.value == self.comboBox_field.value and \
            other.dropdown_columnName.options == self.dropdown_columnName.options and \
            other.dropdown_columnName.value == self.dropdown_columnName.value and \
            other.converterDropdown.value == self.converterDropdown.value:
            return True
        return False

    def getColumnName(self):
        return self.dropdown_columnName.value

    def getFieldName(self):
        return self.comboBox_field.value

    def getCurrentConverter(self):
        " returns dict {'name':value,'params':value}"
        if self.allowConvert:
            return {'name':self.converterDropdown.value.getName(),'params':self.converterDropdown.value.getParams()}
        else:
            return {}

    def setFieldName(self,name:str):
        self.comboBox_field.value = name

    def setColumnName(self,name:str):
        try:
            self.dropdown_columnName.value = name
        except Exception:
            raise Exception("Invalid selection.",name,"not in",self.dropdown_columnName.options)

    def setCurrentConverter(self,converter:dict):
        "exprects dict {'name':value,'params':value}"
        if 'name' in converter and 'params' in converter:
            conv = [e for e in self.availCOnverteroptions if converter['name'] == e[0]][0] 
            self.converterDropdown.value =  conv[1]
            self.converterDropdown.value.setParams( converter['params'])
            

    def setColumnOptions(self,options:list):
        self.dropdown_columnName.options = options

    def on_fieldName_changed(self,b):
        value = self.comboBox_field.value
        if not self.ignoreDateTime and value in self.dateTimeKeys:
            if value == self.dateTimeFieldKey:
                self.converterDropdown.options = [e for e in self.availCOnverteroptions if "datetime" in e[0].lower()]
            elif value == self.dateFieldKey:
                self.converterDropdown.options = [e for e in self.availCOnverteroptions if "date" in e[0].lower() and not "time" in e[0].lower()]
            elif value == self.timeFieldKey:
                self.converterDropdown.options = [e for e in self.availCOnverteroptions if "time" in e[0].lower() and not "date" in e[0].lower()]

        else:
            self.converterDropdown.options = self.availCOnverteroptions

    def on_converter_changed(self,foo):
        if self.allowConvert:
            value = self.converterDropdown.value
            converterSettings = value.getWidget()
            converterSettings.layout=widgets.Layout(width='98%')
            self.converterWidgetConainer.children = [self.converterDropdown,converterSettings]
            if isinstance(value,WidgetConstConverterBase):
                self.dropdown_columnName.disabled = True
            else:
                self.dropdown_columnName.disabled = False
            self.on_fieldName_changed(0)



# Converter widgets ####################################################################
 
class WidgetConverterBase(abc.ABC):
    """ base of container that holds a convert function and a corresponding widget"""
    def __init__(self, converter:miqtconv.ConverterBase, name="undefined"):
        #super().__init__(name)
        self._converter = converter
        self._converter._name = name
        self._widget = None
    
    def getWidget(self):
        """ returns converter widget"""
        return self._widget

    def convert(self,value:str) -> str:
        self._converter.setParams(self.getParams())
        return self._converter.convert(value)

    def setParams(self,params):
        self._converter.setParams(params)
        self.setWidgetParams(params)

    def getParams(self):
        return self.getWidgetParams()

    def getName(self):
        return self._converter.getName()

    @abc.abstractmethod
    def setWidgetParams(self,params):
        pass

    @abc.abstractmethod
    def getWidgetParams(self):
        pass

    @staticmethod
    def getAllConverters(baseClass):
        """ Gets all non abstract sub classes """
        subClasses = []
        for subClass in baseClass.__subclasses__():
            if not inspect.isabstract(subClass):
                subClasses.append(subClass)
            subClasses += WidgetConverterBase.getAllConverters(subClass)
        return subClasses


class WidgetConstConverterBase(WidgetConverterBase):#,abc.ABC):
    """ base class for const converters. For children of this class the colum header selector is disabled in FileParserWidget """
    def __init__(self,converter_:miqtconv.ConverterBase, name="undefined"):
        super().__init__(converter_, name)
    @abc.abstractmethod
    def foo(self):
        """ just to make me abstract """
        pass

class WidgetNoneConverter(WidgetConverterBase):
    """ Converter that does nothing """
    def __init__(self):
        super().__init__(miqtconv.NoneConverter(),"None")
        self._widget = widgets.VBox([])

    def setWidgetParams(self,params):
        pass

    def getWidgetParams(self):
        pass


class WidgetRad2DegreeConvert(WidgetConverterBase):
    def __init__(self):
        super().__init__(miqtconv.Rad2DegreeConvert(),"Rad2Degree")
        self._widget = widgets.VBox([])

    def setWidgetParams(self,params):
        pass

    def getWidgetParams(self):
        pass


class WidgetDateConverter(WidgetConverterBase):
    def __init__(self):
        super().__init__(miqtconv.DateConverter(),"Date")
        self.formatWidget = widgets.Text(layout=widgets.Layout(width='188px'),placeholder = "e.g: %d.%m.%Y",value = "%d.%m.%Y")
        self._widget =  widgets.VBox([widgets.Label("Format:"),self.formatWidget])
         
    def setWidgetParams(self,params):
        self.formatWidget.value = params

    def getWidgetParams(self):
        return self.formatWidget.value

    def __copy__(self): # for some reason deepcopy converter fails. Maybe this can be implemented in base class?
        return WidgetDateConverter()


class WidgetTimeConverter(WidgetConverterBase):
    def __init__(self):
        super().__init__(miqtconv.TimeConverter(),"Time")
        self.formatWidget = widgets.Text(layout=widgets.Layout(width='188px'),placeholder = "e.g: %H:%M:%S.%f",value = "%H:%M:%S.%f")
        self._widget =  widgets.VBox([widgets.Label("Format:"),self.formatWidget])

    def setWidgetParams(self,params):
        self.formatWidget.value = params

    def getWidgetParams(self):
        return self.formatWidget.value

    def __copy__(self): # for some reason deepcopy converter fails. Maybe this can be implemented in base class?
        return WidgetTimeConverter()


class WidgetDateTimeConverter(WidgetConverterBase):
    def __init__(self):
        super().__init__(miqtconv.DateTimeConverter(),"DateTime")
        self.formatWidget = widgets.Text(layout=widgets.Layout(width='188px'),placeholder = "e.g: %d.%m.%Y %H:%M:%S.%f",value = miqtv.date_formats["mariqt"])
        self._widget =  widgets.VBox([widgets.Label("Format:"),self.formatWidget])

    def setWidgetParams(self,params):
        self.formatWidget.value = params

    def getWidgetParams(self):
        return self.formatWidget.value

    def __copy__(self): # for some reason deepcopy converter fails. Maybe this can be implemented in base class?
        return WidgetDateTimeConverter()


class WidgetUnixDateTimeConverter(WidgetConverterBase):
    def __init__(self):
        super().__init__(miqtconv.UnixDateTimeConverter(),"Unix DateTime")
        self._widget =  widgets.VBox([])

    def setWidgetParams(self,params):
        pass

    def getWidgetParams(self):
        pass

    def __copy__(self): # for some reason deepcopy converter fails. Maybe this can be implemented in base class?
        return WidgetUnixDateTimeConverter()


class WidgetDateSince1970Converter(WidgetConverterBase):
    def __init__(self):
        super().__init__(miqtconv.DateSince1970Converter(),"Date days since 1970")
        self._widget =  widgets.VBox([])
         
    def setWidgetParams(self,params):
        pass

    def getWidgetParams(self):
        pass

    def __copy__(self): # for some reason deepcopy converter fails. Maybe this can be implemented in base class?
        return WidgetDateSince1970Converter()

class WidgetDoubleMinMaxConverter(WidgetConverterBase):
    """ Set values outside min max range to None """
    def __init__(self):
        super().__init__(miqtconv.DoubleMinMaxConverter(),"Double Min Max Converer")
        self.minWidget = widgets.FloatText(description='Min')
        self.maxWidget = widgets.FloatText(description='Max')
        self._widget = widgets.VBox([self.minWidget,self.maxWidget])

    def setWidgetParams(self,params):
        self.minWidget.value = params[0]
        self.maxWidget.value = params[1]

    def getWidgetParams(self):
        return [self.minWidget.value,self.maxWidget.value]

    def __copy__(self): # for some reason deepcopy converter fails. Maybe this can be implemented in base class?
        return WidgetDoubleMinMaxConverter()


class WidgetDoubleConstOffsetConverter(WidgetConverterBase):
    """ add a const offset to value """
    def __init__(self):
        super().__init__(miqtconv.DoubleConstOffsetConverter(),"Double Const Offset Converter")
        self._widget = widgets.FloatText()

    def setWidgetParams(self,params):
        self._widget.value = params

    def getWidgetParams(self):
        return self._widget.value

    def __copy__(self): # for some reason deepcopy converter fails. Maybe this can be implemented in base class?
        return WidgetDoubleConstOffsetConverter()


class WidgetDoubleMinMaxAndOffsetConverter(WidgetConverterBase):
    """ Set values outside min max range to None and add const offset if not None """
    def __init__(self):
        super().__init__(miqtconv.DoubleMinMaxAndOffsetConverter(),"Double Min Max + Offset Converer")
        self.widgetMinMaxConverter = WidgetDoubleMinMaxConverter()
        self.widgetOffsetConverter = WidgetDoubleConstOffsetConverter()
        self._widget = widgets.VBox([self.widgetMinMaxConverter._widget,self.widgetOffsetConverter._widget])

    def setWidgetParams(self,params):
        self.widgetMinMaxConverter.setParams(params[0])
        self.widgetOffsetConverter.setParams(params[1])

    def getWidgetParams(self):
        return [self.widgetMinMaxConverter.getParams(),self.widgetOffsetConverter.getParams()]

    def __copy__(self): # for some reason deepcopy converter fails. Maybe this can be implemented in base class?
        return WidgetDoubleMinMaxAndOffsetConverter()


class WidgetDoubleConstFactorConverter(WidgetConverterBase):
    """ multiply with const offset to value """
    def __init__(self):
        super().__init__(miqtconv.DoubleConstFactorConverter(),"Double Const Factor Converter")
        self._widget = widgets.FloatText()

    def setWidgetParams(self,params):
        self._widget.value = params

    def getWidgetParams(self):
        return self._widget.value

    def __copy__(self): # for some reason deepcopy converter fails. Maybe this can be implemented in base class?
        return WidgetDoubleConstFactorConverter()


### Const converters

class WidgetConstDoubleConverter(WidgetConstConverterBase):
    """ returns const value """
    def __init__(self):
        super().__init__(miqtconv.ConstDoubleConverter(),"Const Double")
        self._widget = widgets.FloatText()

    def setWidgetParams(self,params):
        self._widget.value = params

    def getWidgetParams(self):
        return self._widget.value

    def foo(self):
        pass

    def __copy__(self): # for some reason deepcopy converter fails. Maybe this can be implemented in base class?
        return WidgetConstDoubleConverter()


class WidgetConstDateConverter(WidgetConstConverterBase):
    def __init__(self):
        super().__init__(miqtconv.ConstDateConverter(),"Const Date")
        self._widget = widgets.DatePicker(value=datetime.date(2020,1,1))

    def setWidgetParams(self,params):
        "date in %Y-%m-%d"
        self._widget.value = datetime.datetime.strptime(params,miqtv.date_formats["mariqt"].split(" ")[0])

    def getWidgetParams(self):
        return self._widget.value.strftime(miqtv.date_formats["mariqt"].split(" ")[0])

    def foo(self):
        pass

    def __copy__(self): # for some reason deepcopy converter fails. Maybe this can be implemented in base class?
        return WidgetConstDateConverter()

class WidgetConstTimeConverter(WidgetConstConverterBase):
    def __init__(self):
        super().__init__(miqtconv.ConstTimeConverter(),"Const Time")
        dots = widgets.Label(":")
        self.hourWidget = widgets.BoundedIntText(value=0,min=0,max=23,step=1,layout=widgets.Layout(width='50px'))
        self.minuteWidget = widgets.BoundedIntText(value=0,min=0,max=59,step=1,layout=widgets.Layout(width='50px'))
        self.secondWidget = widgets.BoundedIntText(value=0,min=0,max=59,step=1,layout=widgets.Layout(width='50px'))
        timeWidget = widgets.HBox([self.hourWidget,dots,self.minuteWidget,dots,self.secondWidget],layout=widgets.Layout(width='auto'))
        self._widget = timeWidget

    def setWidgetParams(self,params):
        "time in %H:%M:%S.f"
        dt = datetime.datetime.strptime(params,miqtv.date_formats["mariqt"].split(" ")[1])
        self.hourWidget.value = dt.hour
        self.minuteWidget.value = dt.minute
        self.secondWidget.value = dt.second
        # msec is ignored

    def getWidgetParams(self):
        dt = datetime.time(self.hourWidget.value,self.minuteWidget.value,self.secondWidget.value)
        return dt.strftime(miqtv.date_formats["mariqt"].split(" ")[1])

    def foo(self):
        pass

    def __copy__(self): # for some reason deepcopy converter fails. Maybe this can be implemented in base class?
        return WidgetConstTimeConverter()

class WidgetConstDateTimeConverter(WidgetConstConverterBase):
    def __init__(self):
        super().__init__(miqtconv.ConstDateTimeConverter(),"Const DateTime")
        self.constDateConverter = WidgetConstDateConverter()
        self.dateWidget = self.constDateConverter._widget
        self.constTimeConverter = WidgetConstTimeConverter()
        self.timeWidget = self.constTimeConverter._widget
        self._widget = widgets.VBox([self.dateWidget,self.timeWidget],layout=widgets.Layout(width='auto'))

    def convert(self, value: str) -> str:
        dt = datetime.datetime.strptime(self.getWidgetParams(),miqtv.date_formats["mariqt"])
        return dt.strftime(miqtv.date_formats["mariqt"])

    def setWidgetParams(self,params):
        "date time in %Y-%m-%d %H:%M:%S.%f"
        self.constDateConverter.setWidgetParams(params.split(" ")[0])
        self.constTimeConverter.setWidgetParams(params.split(" ")[1])

    def getWidgetParams(self):
        return self.constDateConverter.getWidgetParams() + " " + self.constTimeConverter.getWidgetParams()

    def foo(self):
        pass

    def __copy__(self): # for some reason deepcopy converter fails. Maybe this can be implemented in base class?
        return WidgetConstDateTimeConverter()

##############################################################################


class FileParserDateTimeWidget(FileParserWidget):
    
    def __init__(self,defaultFields:dict,on_change_fct,dateTimeParser=[],iFDO=None,allowCustomFields=True,defaultSettings:list=None):
        converters = [ e() for e in WidgetConverterBase.getAllConverters(WidgetConverterBase)]
        FileParserWidget.__init__(self,defaultFields,on_change_fct,requiredFields=[],iFDO=None,ignoreDateTime=False,allowConvert=True,converters=converters,allowCustomFields=allowCustomFields,defaultSettings=defaultSettings)

class FileParserDateTimeWidgetWithMasterTime(FileParserWidget):

    def __init__(self,defaultFields:dict,on_change_fct,dateTimeParser=[],iFDO=None,allowCustomFields=True,instancesList=None,defaultSettings:list=None):
        converters = [ e() for e in WidgetConverterBase.getAllConverters(WidgetConverterBase)]
        FileParserWidget.__init__(self,defaultFields,on_change_fct,requiredFields=[],iFDO=None,ignoreDateTime=False,allowConvert=True,converters=converters,allowCustomFields=allowCustomFields,defaultSettings=defaultSettings)

        self.isMasterTimeRadioButton = widgets.Checkbox(description='Master Time',indent=False)
        self.isMasterTimeRadioButton.observe(self.on_isMasterTimeRadioButton_changed)
        self.id = id(self)
        self.good = True

        self.instancesList = instancesList
        if instancesList is None:
            self.instancesList = []

    def delete(self):
        self.good = False
        if not self.__checkMaster():
            for inst in self.instancesList:
                inst.isMasterTimeRadioButton.value = True
                break

    def copy(self):
        ret = FileParserDateTimeWidgetWithMasterTime(self.defaultFields,self.on_change_fct,allowCustomFields=self.allowCustomFields,instancesList=self.instancesList,defaultSettings=self._defaultSettings)
        ret.setParams(self.getParams())

        self.instancesList.append(ret)
        if not self.__checkMaster():
            ret.isMasterTimeRadioButton.value = True
        else:
            ret.isMasterTimeRadioButton.value = False

        return ret

    def __checkMaster(self):
        masterFound = False
        for inst in self.instancesList:
            if inst.good == True and inst.isMasterTimeRadioButton.value == True:
                masterFound = True
                break
        return masterFound

    def getWidget(self):
        return widgets.VBox([super().getWidget(),self.isMasterTimeRadioButton])

    def on_isMasterTimeRadioButton_changed(self,b):
        if self.isMasterTimeRadioButton.value == True:
            for inst in self.instancesList:
                if inst.good == True and not inst.id == self.id:
                    #pass
                    inst.isMasterTimeRadioButton.value = False
        elif not self.__checkMaster():
            for inst in self.instancesList:
                if inst.good == True and not inst.id == self.id:
                    inst.isMasterTimeRadioButton.value = True
                    break

    def isMasterTime(self):
        return self.isMasterTimeRadioButton.value


#################################################################################################################


class customExiftoolPathChooser():
    """ use .getWidget to get widget """
    def __init__(self):
        self.exiftoolPathChooser = FileChooserPaste()
        self.exiftoolPathChooser.register_callback(self.on_exiftoolPath_selected)
        self.exiftoolPathChooser.show_only_dirs = True
        self.exiftoolConfigAccordion = widgets.Accordion(children=[self.exiftoolPathChooser.getWidget()], selected_index=None)
        self.exiftoolConfigAccordion.set_title(0,"Custom Exifool path")

    def on_exiftoolPath_selected(self,foo=None):
        path = self.exiftoolPathChooser.selected
        miqtv.setExiftoolPath(path)

    def getWidget(self):
        return self.exiftoolConfigAccordion
