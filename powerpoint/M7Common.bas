Attribute VB_Name = "M7Common"
Option Explicit

Option Compare Text

Option Private Module

'======================================================================================
'
' Module containing frequently used code
'
'======================================================================================

'======================================================================================
'
' Browse for a file
'
'======================================================================================
'
' Parameters
'
'   FilterDescription - type or content of file
'   FilterExts - file type(s)
'   Title - heading on FileDialog
'   InitialFolder - as it says - initial folder to start the search
'
'======================================================================================
Function BrowseFile(ByVal FilterDescrip As String, ByVal FilterExts As String, ByVal Title As String, Optional ByVal InitialFolder As String = vbNullString) As String

#If Mac Then

    Dim sMacScript              As String
    Dim sRootFolder             As String


    BrowseFile = MacScript(fncMacScript(FilterDescrip, FilterExts, Title, InitialFolder))
  
    If BrowseFile = "-43" Or BrowseFile = "-1700" Then
        sRootFolder = MacScript("return(path to documents folder) as string")
        BrowseFile = MacScript(fncMacScript(FilterDescrip, FilterExts, Title, sRootFolder))
    End If

#Else

    Dim fdFile          As FileDialog
    Dim sFn             As String

    Set fdFile = Application.FileDialog(msoFileDialogFilePicker)

    With fdFile
        If Len(InitialFolder) > 0 Then .InitialFileName = InitialFolder
        .Filters.Clear
        .Filters.Add Description:=FilterDescrip, Extensions:=FilterExts
        .AllowMultiSelect = False
        .Title = Title
        If .Show = -1 Then
            sFn = .SelectedItems(1)
        Else
            sFn = vbNullString
        End If
    End With

    Set fdFile = Nothing

    BrowseFile = sFn

#End If

End Function

'===================================================================================================

#If Mac Then

Private Function fncMacScript(ByVal FilterDescrip As String, ByVal FilterExts As String, ByVal Title As String, Optional ByVal InitialFolder As String = vbNullString) As String
    
    fncMacScript = "set applescript's text item delimiters to "","" " & vbNewLine & _
        "try " & vbNewLine & _
        "set theFiles to (choose file " & _
        "with prompt ""Please select a " & FilterDescrip & " file"" of type {""" & FilterExts & """} default location alias """ & _
        InitialFolder & """ multiple selections allowed false) as string" & vbNewLine & _
        "set applescript's text item delimiters to """" " & vbNewLine & _
        "on error errStr number errorNumber" & vbNewLine & _
        "return errorNumber " & vbNewLine & _
        "end try " & vbNewLine & _
        "return theFiles"

End Function

#End If

'===================================================================================================
#If Mac Then

Function FileExists(ByVal FileStr As String) As Boolean
' adapted from
'Ron de Bruin : 26-June-2015
'Function to test whether a file or folder exist on a Mac in office 2011 and up
'Uses AppleScript to avoid the problem with long names in Office 2011,
'limit is max 32 characters including the extension in 2011.

    Dim ScriptToCheckFile As String
    Dim TestStr As String
    

    If Val(Application.Version) < 15 Then
        ScriptToCheckFile = "tell application " & Chr(34) & "System Events" & Chr(34) & _
         "to return exists disk item (" & Chr(34) & FileStr & Chr(34) & " as string)"
        FileExists = MacScript(ScriptToCheckFile)
    Else
        TestStr = vbNullString
        On Error Resume Next
        TestStr = Dir(FileStr)
        On Error GoTo 0
        If Len(TestStr) > 0 Then FileExists = True
    End If
    
End Function

#Else

Function FileExists(ByVal FileStr As String) As Boolean

FileExists = False
If Len(Dir(FileStr)) > 0 Then FileExists = True

End Function

#End If

'===================================================================================================
'
' Required for Excel 2016 and later on a Mac
'
'===================================================================================================
'Function grantFileAccess(filePermissionCandidates)
'  grantFileAccess = GrantAccessToMultipleFiles(filePermissionCandidates) 'returns true if access granted, false otherwise_
'End Function

'===================================================================================================
'
' get a column number given a range for the headings and the heading
'
'===================================================================================================
Function ColNoA(sHeadings() As String, sHeading As String) As Long

Dim lCol            As Long
Dim lColMax         As Long
Dim lColMin         As Long
Dim sHdg            As String

'lColMax = rHeadings.Columns.Count
lColMax = UBound(sHeadings)

For lCol = 0 To lColMax
    sHdg = sHeadings(lCol)
    If sHdg = sHeading Or sHdg = Chr(149) & Chr(200) & Chr(192) & sHeading Then
        ColNoA = lCol
        Exit Function
    End If
Next lCol

ColNoA = -1

End Function

'------------------------------------------------------------------------------------------------------
Function ColNoXA(sHeadings() As String, ParamArray sHeading() As Variant) As Long

Const sONE                  As String = "1"
Const sTWO                  As String = "2"

Dim sTmpHdg                 As String

Dim lIndx                   As Long
Dim lMin                    As Long
Dim lMax                    As Long

lMin = LBound(sHeading)
lMax = UBound(sHeading)

For lIndx = lMin To lMax
    sTmpHdg = CStr(sHeading(lIndx))
    ColNoXA = ColNoA(sHeadings, sTmpHdg)
    If ColNoXA >= 0 Then Exit Function
    ColNoXA = ColNoA(sHeadings, sTmpHdg & sONE)
    If ColNoXA >= 0 Then Exit Function
    ColNoXA = ColNoA(sHeadings, sTmpHdg & sTWO)
    If ColNoXA >= 0 Then Exit Function
Next lIndx

End Function

'===================================================================================================
'
' set the path
'
'===================================================================================================
Sub SetPath(ByVal NewPath As String)

On Error Resume Next
ChDir NewPath
On Error Resume Next
ChDir NewPath

End Sub

'===================================================================================================
'
' get a column number given a range for the headings and the heading
'
'===================================================================================================
Function ColNo(rHeadings As Range, sHeading As String) As Long

Dim lCol            As Long
Dim lColMax         As Long
Dim sHdg            As String

lColMax = rHeadings.Columns.Count

For lCol = 1 To lColMax
    sHdg = rHeadings.Cells(1, lCol)
    If sHdg = sHeading Or sHdg = Chr(149) & Chr(200) & Chr(192) & sHeading Then
        ColNo = lCol
        Exit Function
    End If
Next lCol

ColNo = 0

End Function
''
'''------------------------------------------------------------------------------------------------------
''Function ColNoX(rHeadings As Range, ParamArray sHeading() As Variant) As Long
''
''Const sONE                  As String = "1"
''Const sTWO                  As String = "2"
''
''Dim sTmpHdg                 As String
''
''Dim lIndx                   As Long
''Dim lMin                    As Long
''Dim lMax                    As Long
''
''lMin = LBound(sHeading)
''lMax = UBound(sHeading)
''
''For lIndx = lMin To lMax
''    sTmpHdg = CStr(sHeading(lIndx))
''    ColNoX = ColNo(rHeadings, sTmpHdg)
''    If ColNoX <> 0 Then Exit Function
''    ColNoX = ColNo(rHeadings, sTmpHdg & sONE)
''    If ColNoX <> 0 Then Exit Function
''    ColNoX = ColNo(rHeadings, sTmpHdg & sTWO)
''    If ColNoX <> 0 Then Exit Function
''Next lIndx
''
''End Function
''
'''===================================================================================================
'''
''' set the path
'''
'''===================================================================================================
''Sub SetPath(ByVal NewPath As String)
''
''On Error Resume Next
''ChDir NewPath
''On Error Resume Next
''ChDir NewPath
''
''End Sub

'=====================================================================================================
'
' Update custom properties of the created report
'
'=====================================================================================================
Sub UpdateCustomDocProperties(wb As Workbook, ByVal sPropName As String, _
                                ByVal vValue As Variant, _
                                Optional ByVal docType As Office.MsoDocProperties = Office.MsoDocProperties.msoPropertyTypeString)

Dim lErr            As Long

On Error Resume Next
wb.CustomDocumentProperties(sPropName).Value = vValue
lErr = Err.Number
On Error GoTo 0

If lErr > 0 Then
    wb.CustomDocumentProperties.Add _
        Name:=sPropName, _
        LinkToContent:=False, _
        Type:=docType, _
        Value:=vValue
End If

End Sub


'================================================================================================
'
' is the workbook already open?
'
' original code from Ron de Bruin and Ron Bovey
'
'================================================================================================
Function BookIsOpen(ByVal FileName As String) As Boolean

Dim sFn                 As String

sFn = ShortFileName(FileName)

BookIsOpen = False
On Error Resume Next
BookIsOpen = Not (Application.Workbooks(sFn) Is Nothing)
On Error GoTo 0
    
End Function

'=====================================================================================
'
' strip off the path
'
'=====================================================================================
Function ShortFileName(ByVal FileName As String) As String

Dim sSep                As String
Dim lPosn               As Long

If Application.OperatingSystem Like "*mac*" Then
    sSep = ":"
Else
    sSep = "\"
End If

lPosn = InStrRev(FileName, sSep)

If lPosn = 0 Then
    ShortFileName = FileName
Else
    ShortFileName = Right(FileName, Len(FileName) - lPosn)
End If

End Function

'==============================================================================================
'
' like Excel VBA Split except ignores separators between quotes
'
' Expression    - a string to be split up
' Delimiter     - character specifying break between fields, default is a space to be consistent with Split function
' Limit         - maximum number of fields.  If set then get an array with this number of fields irrespective of fields retrieved.
' TextQualifier - the character that says what is following is a single field until we reach another single quote
'
'==============================================================================================
Function OurSplit(ByVal Expression As String, _
            Optional ByVal Delimiter As String = " ", _
            Optional ByVal Limit As Long = -1, _
            Optional ByVal TextQualifier As String = """" _
            ) As String()

Dim sSep                As String
Dim sTextQual           As String
Dim sTextQual2          As String
Dim sTextQualSep        As String

Dim lSepCnt             As Long
Dim lPosn               As Long
Dim lPosn2              As Long
Dim lPosnTq2            As Long
Dim lPosnTq2Too         As Long
Dim lIndx               As Long
Dim sCh                 As String
Dim sFld                As String

Dim sOurSplit()         As String

' remember the match strings

sSep = Left(Delimiter, 1)
sTextQual = Left(TextQualifier, 1)
sTextQual2 = sTextQual & sTextQual
sTextQualSep = sTextQual & sSep

' how big is the output array?

If Limit > 0 Then
    lSepCnt = Limit - 1
Else
    lPosn = 0
    lSepCnt = 0
    Do
        lPosn = InStr(lPosn + 1, Expression, sSep)
        If lPosn = 0 Then Exit Do
        lSepCnt = lSepCnt + 1
    Loop
End If

' actual fields are num of separators plus 1

ReDim sOurSplit(lSepCnt) As String

' set up for working through the input string

lIndx = 0
lPosn = 0

Do While lIndx <= lSepCnt

' first chara is it text qualifier?

    sCh = Mid(Expression, lPosn + 1, 1)
    If sCh = sTextQual Then

' where might the end of the field be?

        lPosn2 = InStr(lPosn + 2, Expression, sTextQualSep)

' no end of field so take to end of string

        If lPosn2 = 0 Then
            sOurSplit(lIndx) = Replace(Right(Expression, Len(Expression) - lPosn - 1), sTextQual2, sTextQual, 1)
            lIndx = lIndx + 1
            Exit Do

' we've found an end of field, but is it tied in with a double quote?

        Else
            Do While Mid(Expression, lPosn2 - 1, 2) = sTextQual2
                If Mid(Expression, lPosn2 - 2, 2) = sTextQual2 Then Exit Do
                lPosn2 = InStr(lPosn + 2, Expression, sTextQualSep)
                If lPosn2 = 0 Then Exit Do
            Loop
            
' did we reach the end of the string?

            If lPosn2 = 0 Then
                sOurSplit(lIndx) = Replace(Right(Expression, Len(Expression) - lPosn - 1), sTextQual2, sTextQual, 1)
                lIndx = lIndx + 1
                Exit Do
            End If
            sOurSplit(lIndx) = Replace(Mid(Expression, lPosn + 2, lPosn2 - lPosn - 2), sTextQual2, sTextQual, 1)
            lIndx = lIndx + 1
            lPosn = lPosn2 + 1
        End If

    Else
        lPosn2 = InStr(lPosn + 1, Expression, sSep)
        If lPosn2 = 0 Then
            sOurSplit(lIndx) = Right(Expression, Len(Expression) - lPosn)
            lIndx = lIndx + 1
            Exit Do
        Else
            sOurSplit(lIndx) = Mid(Expression, lPosn + 1, lPosn2 - lPosn - 1)
            lIndx = lIndx + 1
            lPosn = lPosn2
        End If
    End If
Loop

If lIndx < lSepCnt And Limit <= 0 Then
    ReDim Preserve OurSplit(lIndx - 1) As String
End If

OurSplit = sOurSplit

End Function



