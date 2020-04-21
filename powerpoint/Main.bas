Attribute VB_Name = "Main"

'========================================================================================
'
' Main entry point
'
'========================================================================================
Sub ComplianceDash()

Dim leftPos                     As Single
Dim shTxt                       As String
Dim descTxt                     As String
Dim rgbCol                      As Long
Dim complianceHeadingsRange     As Range
Dim oNewSlide                   As PowerPoint.slide
Dim targetMet As Boolean
Dim targetVal As Long

' remember who we are
Set wbMe = ThisWorkbook

' get assistant data
loadAssistantData

' generate slide
Set oNewSlide = setupPowerPoint()

' create compliance base shapes
leftPos = 17.67
Set complianceHeadingsRange = wbMe.Sheets("Ref").Range("D2:F9")
For Each r In complianceHeadingsRange.Rows
    shTxt = r.Cells(1).Value
    descTxt = r.Cells(2).Value
    rgbCol = CLng(r.Cells(3).DisplayFormat.Interior.Color)
    'Debug.Print VarType(rgbCol)
    CreateBaseRectangle oNewSlide, leftPos, rgbCol, shTxt, descTxt
    leftPos = leftPos + 90.65 + 3.15
Next r

If lTotalRoles = 0 Then targetVal = 0 Else targetVal = 10 ^ Round(Log(lTotalRoles) / 2 - 2, 0)
If targetVal <= 1 Then targetVal = 1

Dim sTopPos As Single: sTopPos = 273.33
Dim sLeftPos As Single: sLeftPos = 22.03
leftOffset = 93.75

' Disclosures
targetMet = gdDataDisclosures >= targetVal
CreateComplianceData oNewSlide, sLeftPos, sTopPos, targetMet, "100%", "98.5%", gdDataDisclosures & "%"
sLeftPos = sLeftPos + leftOffset

' Full Roles
targetMet = glDataFull <= targetVal
CreateComplianceData oNewSlide, sLeftPos, sTopPos, targetMet, "0", targetVal, glDataFull
sLeftPos = sLeftPos + leftOffset


' Getting started modules
cDR = wbMe.Sheets("Ref").Range("B4:B6")
For r = 1 To UBound(cDR)
    If r = 3 Then modCount = "3/4" Else modCount = r
    topOffset = (r - 1) * 69.5
    actVal = cDR(r, 1)
    targetMet = actVal <= targetVal
    CreateComplianceData oNewSlide, sLeftPos, sTopPos + topOffset, targetMet, "0", targetVal, actVal, "Module " & modCount
Next r

' back to normal modules
cDR = wbMe.Sheets("Ref").Range("B7:B10")
For r = 1 To UBound(cDR)
    sLeftPos = sLeftPos + leftOffset
    actVal = cDR(r, 1)
    targetMet = actVal <= targetVal
    CreateComplianceData oNewSlide, sLeftPos, sTopPos, targetMet, "0", targetVal, actVal
Next r

' woodbadges (target is half normal)
sLeftPos = sLeftPos + leftOffset
targetMet = actVal <= targetVal / 2
CreateComplianceData oNewSlide, sLeftPos, sTopPos, True, "0", targetVal / 2, glDataWb


' Setup headings and legends etc.
setupInfo oNewSlide, gsDataDate, gsReportTitle, glTotalAdults, glTotalRoles

' Delete blanking slide
deleteBlankingSlide

Application.ScreenUpdating = True
Application.Calculation = xlCalculationAutomatic
End Sub

Sub loadAssistantData()
Dim fIF                         As InitForm
Dim sFileNameCmp                As String
Dim sFileNameTrg                As String
Dim lDbsPct                     As String
Dim wbInputCmp                  As Workbook
Dim wbInputTrg                  As Workbook
Dim ws                          As Worksheet
Dim wsT                         As Worksheet
Dim wsC                         As Worksheet


' let's get on with it
Set fIF = New InitForm
If fIF.Cancel Then Exit Sub

' no changes to be visible
If Not gbDebug Then Application.ScreenUpdating = False
Application.Calculation = xlCalculationManual
ThisWorkbook.Saved = True

' get the values supplied
sFileNameCmp = fIF.CmpFileName
sFileNameTrg = fIF.TrgFileName
lDbsPct = fIF.tbxDbsPct
gsReportTitle = fIF.tbxRepTtl

' Get rid of the form
Set fIF = Nothing

' is the input already open?

If BookIsOpen(sFileNameCmp) Or BookIsOpen(sFileNameTrg) Then
    iAns = MsgBox(prompt:="A file with the same name as the input file is already open" & vbCrLf & _
                "Can this file be closed so the program can work correctly?", Buttons:=vbYesNo + vbQuestion)
                
    If iAns <> vbYes Then Exit Sub
    
    On Error Resume Next
    Application.Workbooks(ShortFileName(sFileNameCmp)).Close
    Application.Workbooks(ShortFileName(sFileNameTrg)).Close
    On Error GoTo 0
End If

On Error Resume Next
Set wbInputCmp = Workbooks.Open(FileName:=sFileNameCmp, ReadOnly:=True)
Set wbInputTrg = Workbooks.Open(FileName:=sFileNameTrg, ReadOnly:=True)
'lErr = Err.Number
'sErr = Err.Description
On Error GoTo 0

gsDataDate = Format(CDate(wbInputCmp.Sheets(1).Range("C5")), "mmmm yyyy")

Set ws = wbMe.Sheets("Ref")
Set wsT = wbInputTrg.Sheets(2)
Set wsC = wbInputCmp.Sheets(2)

getComplianceData ws, wsC, wsT

' finished with the input file
wbInputTrg.Close savechanges:=False
Set wbInputTrg = Nothing
wbInputCmp.Close savechanges:=False
Set wbInputCmp = Nothing

End Sub

Sub getComplianceData(ws As Worksheet, wsC As Worksheet, wsT As Worksheet)
Dim lOdueGDPR As Long
Dim lOdueFull As Long
Dim lOdueM01Ex As Long
Dim lOdueM01 As Long
Dim lOdueM02 As Long
Dim lOdueM03 As Long
Dim lOdueM04 As Long
Dim lOdueSecWb As Long
Dim lOdueManWb As Long
Dim lOdueFA As Long
Dim lOdueSfty As Long
Dim lOdueSafe As Long


' Values from Training Assistant Report
lOdueM01Ex = wsT.Range("D4").Value  ' Overdue M01EX (Getting Started for Trustees)
lOdueGDPR = wsT.Range("D5").Value   ' Overdue GDPR

' Finished with worksheet
Set wsT = Nothing

' Values from Compliance Assistant Report
lOdueFull = wsC.Range("K14").Value  ' Overdue Full role
lOdueM01 = wsC.Range("K22").Value   ' Overdue M01 (Getting Started)
lOdueM02 = wsC.Range("K28").Value   ' Overdue M02 (Personal Learning Plan)
lOdueM03 = wsC.Range("K26").Value   ' Overdue M03 (Tools for the Role - Leaders)
lOdueM04 = wsC.Range("K27").Value   ' Overdue M04 (Tools for the Role - Managers)
lOdueSecWb = wsC.Range("K32").Value ' Overdue Section Woodbadge
lOdueManWb = wsC.Range("K33").Value ' Overdue Manager Woodbadge
lOdueFA = wsC.Range("K35").Value    ' Overdue First Aid MOL
lOdueSfty = wsC.Range("K36").Value  ' Overdue Safety MOL
lOdueSafe = wsC.Range("K37").Value  ' Overdue Safeguarding MOL

glTotalAdults = wsC.Range("E13").Value   ' Total Adults in report
glTotalRoles = wsC.Range("E14").Value    ' Total Roles in report

' Finished with worksheet
Set wsC = Nothing

gdDataDisclosures = lDbsPct
glDataFull = lOdueFull
glDataM01 = lOdueM01 + lOdueM01Ex
glDataM02 = lOdueM02
glDataM034 = lOdueM03 + lOdueM04
glDataGDPR = lOdueGDPR
glDataSfty = lOdueSfty
glDataSafe = lOdueSafe
glDataFA = lOdueFA
glDataWb = lOdueSecWb + lOdueManWb

ws.Range("B2").Value = gdDataDisclosures
ws.Range("B3").Value = glDataFull
ws.Range("B4").Value = glDataM01
ws.Range("B5").Value = glDataM02
ws.Range("B6").Value = glDataM034
ws.Range("B7").Value = glDataGDPR
ws.Range("B8").Value = glDataSfty
ws.Range("B9").Value = glDataSafe
ws.Range("B10").Value = glDataFA
ws.Range("B11").Value = glDataWb

ws.Range("B12").Value = glTotalAdults
ws.Range("B13").Value = glTotalRoles

End Sub
