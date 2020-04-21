VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "ThisWorkbook"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Private Sub Workbook_Open()

Dim ws                      As Worksheet
Dim lCurrVer                As Long
Dim iAns                    As Integer

Application.ScreenUpdating = False

With ThisWorkbook
    .Sheets("Front").Visible = True
    .Sheets("Front").Activate
    .Saved = True
End With

Application.ScreenUpdating = True

End Sub

