VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} InitForm 
   Caption         =   "Compliance Dashboard Generator"
   ClientHeight    =   6150
   ClientLeft      =   120
   ClientTop       =   465
   ClientWidth     =   11760
   OleObjectBlob   =   "InitForm.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "InitForm"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Public Cancel               As Boolean
Public CmpFileName          As String
Public TrgFileName          As String

' values to remember

Dim mlBackColor             As Long
Dim mlCbxColor              As Long

'================================================================================
'
' if the user wants to select a compliance assistant file
'
'================================================================================

Private Sub cmbBrowseCmp_Click()

Dim sTmp                    As String
Dim sSavePath               As String
Dim iAns                    As Integer

sSavePath = CurDir

' preproccessor directive
#If Mac Then

    sTmp = BrowseFile("Excel File", "com.microsoft.excel.xls", "Compliance Assistant Excel File", Me.tbxCmpAsstRepFile)

#Else

    sTmp = BrowseFile("Excel File", "*.xlsx", "Compliance Assistant Excel File", Me.tbxCmpAsstRepFile)
    
#End If

SetPath sSavePath

If Len(sTmp) > 0 And FileExists(sTmp) Then

    Me.tbxCmpAsstRepFile = sTmp

    Call tbxCmpAsstRepFile_AfterUpdate
            
End If

End Sub

'================================================================================
'
' if the user wants to select a training assistant file
'
'================================================================================

Private Sub cmbBrowseTrg_Click()

Dim sTmp                    As String
Dim sSavePath               As String
Dim iAns                    As Integer

sSavePath = CurDir

' preproccessor directive
#If Mac Then

    sTmp = BrowseFile("Excel File", "com.microsoft.excel.xls", "Training Assistant Excel File", Me.tbxTrgAsstRepFile)

#Else

    sTmp = BrowseFile("Excel File", "*.xlsx", "Training Assistant Excel File", Me.tbxTrgAsstRepFile)
    
#End If

SetPath sSavePath

If Len(sTmp) > 0 And FileExists(sTmp) Then

    Me.tbxTrgAsstRepFile = sTmp

    Call tbxTrgAsstRepFile_AfterUpdate
            
End If

End Sub

'================================================================================
'
' when the user changes the compliance assistant file
'
'================================================================================
Private Sub tbxCmpAsstRepFile_AfterUpdate()

If Len(Trim(Me.tbxCmpAsstRepFile)) = 0 Or Not FileExists(Me.tbxCmpAsstRepFile) Then
    Me.tbxCmpAsstRepFile.BackColor = vbRed
Else
    Me.tbxCmpAsstRepFile.BackColor = mlBackColor
End If

End Sub

'================================================================================
'
' when the user changes the training assistant file
'
'================================================================================

Private Sub tbxTrgAsstRepFile_AfterUpdate()

If Len(Trim(Me.tbxTrgAsstRepFile)) = 0 Or Not FileExists(Me.tbxTrgAsstRepFile) Then
    Me.tbxTrgAsstRepFile.BackColor = vbRed
Else
    Me.tbxTrgAsstRepFile.BackColor = mlBackColor
End If

End Sub

'================================================================================
Private Sub tbxDbsPct_Change()

If Me.tbxDbsPct >= 100 Then Me.tbxDbsPct = 100
If Me.tbxDbsPct <= 0 Then Me.tbxDbsPct = 0

End Sub

'================================================================================
Private Sub tbxDbsPct_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
    Select Case KeyAscii
        Case 46
            If InStr(1, tbxDbsPct, ".") > 0 Then KeyAscii = 0
        Case 48 To 57
        Case Else
            KeyAscii = 0
    End Select
End Sub

'================================================================================
'
' Cancel
'
'================================================================================
Private Sub cmbCancel_Click()

Me.Cancel = True
Me.Hide

End Sub

'================================================================================
'
' Are we good to go?
'
'================================================================================
Private Sub cmbOK_Click()

Dim bOK             As Boolean
Dim sError          As String
Const sFILEERROR    As String = "Invalid file"

' say OK until we know better
bOK = True
sError = vbNullString

If Len(Me.tbxTrgAsstRepFile) = 0 Or Not FileExists(Me.tbxTrgAsstRepFile) _
    Or Len(Me.tbxCmpAsstRepFile) = 0 Or Not FileExists(Me.tbxCmpAsstRepFile) Then
    
    bOK = False
    sError = sFILEERROR
End If

' still good to go?

If bOK Then
    ' remember the file for next time
    Me.CmpFileName = Me.tbxCmpAsstRepFile
    Me.TrgFileName = Me.tbxTrgAsstRepFile
    
    SaveSetting gsOURNAME, gsSETUP, gsKeyFILECOMPLIANCE, Me.tbxCmpAsstRepFile
    SaveSetting gsOURNAME, gsSETUP, gsKeyFILETRAINING, Me.tbxTrgAsstRepFile
    SaveSetting gsOURNAME, gsSETUP, gsKeyDBSPCT, Me.tbxDbsPct
    SaveSetting gsOURNAME, gsSETUP, gsKeyRPTTITLE, Me.tbxRepTtl
    
    Me.Cancel = False
    Me.Hide
    Exit Sub
End If

Me.lblError = sError
Me.lblError.Visible = True
    
End Sub

'================================================================================
'
' Initialise and show the form
'
'================================================================================
Private Sub UserForm_Initialize()

' remember the text box backcolor
mlBackColor = Me.tbxCmpAsstRepFile.BackColor


' do we have a file from before?

Me.tbxCmpAsstRepFile = GetSetting(gsOURNAME, gsSETUP, gsKeyFILECOMPLIANCE, "?")
If Me.tbxCmpAsstRepFile = "?" Then Me.tbxCmpAsstRepFile = vbNullString

Me.tbxTrgAsstRepFile = GetSetting(gsOURNAME, gsSETUP, gsKeyFILETRAINING, "?")
If Me.tbxTrgAsstRepFile = "?" Then Me.tbxTrgAsstRepFile = vbNullString

' only file on windows as need permission on a Mac (Aggghhh)

If Not Application.OperatingSystem Like "*mac*" Then Call tbxTrgAsstRepFile_AfterUpdate
If Not Application.OperatingSystem Like "*mac*" Then Call tbxCmpAsstRepFile_AfterUpdate

Me.tbxDbsPct = GetSetting(gsOURNAME, gsSETUP, gsKeyDBSPCT, 98.2)
Me.tbxRepTtl = GetSetting(gsOURNAME, gsSETUP, gsKeyRPTTITLE, "?")
If Me.tbxRepTtl = "?" Then Me.tbxRepTtl = vbNullString


' hello world!
Me.lblError.Visible = False
Me.Show

End Sub
