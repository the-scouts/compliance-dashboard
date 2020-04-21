Attribute VB_Name = "PPT"
Public Function setupPowerPoint() As PowerPoint.slide

Dim oNewPP          As PowerPoint.Application
Dim oCurPres        As PowerPoint.Presentation
Dim oNewSlide       As PowerPoint.slide

' Look for existing instance
On Error Resume Next
Set oNewPP = GetObject(, "PowerPoint.Application")
On Error GoTo 0

' If no existing instance create new
If oNewPP Is Nothing Then
    Set oNewPP = New PowerPoint.Application
End If

' Create new presentation & get it
'If oNewPP.Presentations.Count = 0 Then
    oNewPP.Presentations.Add
'End If
Set oCurPres = oNewPP.ActivePresentation

' Set slide size
oCurPres.PageSetup.SlideSize = ppSlideSizeA4Paper

' Add slide with blank layout
oCurPres.Slides.Add oCurPres.Slides.Count + 1, ppLayoutBlank
Set oNewSlide = oCurPres.Slides(oCurPres.Slides.Count)

' Add blanking slide
oCurPres.Slides.Add oCurPres.Slides.Count + 1, ppLayoutBlank

' Go to new slide
oNewPP.ActiveWindow.View.GotoSlide oCurPres.Slides.Count

Set setupPowerPoint = oNewSlide

' Clean up
'AppActivate ("PowerPoint")
Set activeSlide = Nothing
Set newPowerPoint = Nothing

End Function

Public Sub deleteBlankingSlide()

Dim oNewPP          As PowerPoint.Application
Dim oCurPres        As PowerPoint.Presentation
Dim oSlide       As PowerPoint.slide

' Look for existing instance
Set oPP = GetObject(, "PowerPoint.Application")
Set oCurPres = oPP.ActivePresentation
Set oSlide = oCurPres.Slides(oCurPres.Slides.Count)

' Delete slide
oSlide.Delete

' Clean up
Set oNewPP = Nothing
Set oCurPres = Nothing
Set oSlide = Nothing

End Sub

Public Sub CreateBaseRectangle(slide As PowerPoint.slide, leftPos As Single, fillColour As Long, subHead As String, desc As String)
Dim oSh As PowerPoint.Shape

Set oSh = slide.Shapes.AddShape(msoShapeRoundedRectangle, Left:=leftPos, Top:=142.75, Width:=90.65, Height:=329)
With oSh
    .Name = "Rounded Rectangle - " & subHead
    .Fill.ForeColor.RGB = fillColour
    .Line.ForeColor.RGB = fillColour
    With .TextFrame
        .VerticalAnchor = msoAnchorTop
        With .TextRange
            .Text = subHead & vbNewLine _
                & vbNewLine _
                & desc
            .ParagraphFormat.Alignment = ppAlignLeft
            
            ' Set main body font
            With .Font
                .Name = "Nunito Sans"
                .Size = 8.12
            End With
            
            ' Set heading font
            With .Paragraphs(1)
                .Font.Name = "Nunito Sans Black"
                .Font.Size = 8.95
            End With
            
            ' Set spacing font
            .Paragraphs(2).Font.Size = 11
        End With        ' TextRange
    End With            ' TextFrame
End With                ' oSh, the shape itself

End Sub

Public Sub CreateTextHeader(slide As PowerPoint.slide, topPos As Single, fontSize As Single, headingText As String)
Dim oSh As PowerPoint.Shape

Set oSh = slide.Shapes.AddTextbox(msoTextOrientationHorizontal, Left:=17.67, Top:=topPos, Width:=435, Height:=34.837)
With oSh
    .Name = "Text (" & headingText & ")"
    With .TextFrame.TextRange
        .Text = headingText
        With .Font
            .Name = "Nunito Sans Black"
            .Size = fontSize
            .Color = RGB(116, 20, 220)
        End With    ' Font
    End With        ' TextRange
End With            ' oSh, the shape itself

End Sub

Public Sub CreateLegend(slide As PowerPoint.slide, leftPos As Single, topPos As Single, legendText As String)
Dim oSh As PowerPoint.Shape

Set oSh = slide.Shapes.AddTextbox(msoTextOrientationHorizontal, Left:=leftPos, Top:=topPos, Width:=119.24, Height:=17.60528)
With oSh
    .Name = "Legend (" & legendText & ")"
    With .TextFrame.TextRange
        .Text = legendText
        With .Font
            .Name = "Nunito Sans"
            .Size = 8.53
        End With    ' Font
    End With        ' TextRange
End With            ' oSh, the shape itself

End Sub


Public Sub CreateComplianceData(slide As PowerPoint.slide, leftPos As Single, topPos As Single, targetMet As Boolean, sAim As String, sTarget As Variant, sActual As Variant, Optional sHead As String)
Dim oSh As PowerPoint.Shape
Dim actualCol As Long: actualCol = RGB(192, 0, 0) ' default red
If targetMet Then actualCol = RGB(35, 169, 80)      ' green if target is met

' Target
Set oSh = slide.Shapes.AddShape(msoShapeRoundedRectangle, Left:=leftPos, Top:=topPos, Width:=81.59, Height:=21.62)
With oSh
    .Name = "Data - Objectives"
    .Fill.ForeColor.RGB = RGB(255, 255, 255)
    .Line.ForeColor.RGB = RGB(231, 230, 230)
    With .TextFrame.TextRange
        .Text = "Aim: " & sAim & " (T " & sTarget & ")"
        .ParagraphFormat.Alignment = ppAlignLeft
        With .Font
            .Name = "Nunito Sans"
            .Size = 7.31
            .Color = RGB(0, 0, 0)
        End With    ' Font
    End With        ' TextRange
End With            ' oSh, the shape itself

' Actual
Set oSh = slide.Shapes.AddShape(msoShapeRoundedRectangle, Left:=leftPos, Top:=topPos + 21.62, Width:=81.59, Height:=21.62)
With oSh
    .Name = "Data - Actual"
    .Fill.ForeColor.RGB = actualCol
    .Line.ForeColor.RGB = actualCol
    With .TextFrame.TextRange
        .Text = "Actual: " & sActual
        .ParagraphFormat.Alignment = ppAlignLeft
        With .Font
            .Name = "Nunito Sans"
            .Size = 7.31
        End With    ' Font
    End With        ' TextRange
End With            ' oSh, the shape itself

' Possible header
If Len(sHead) > 0 Then
Set oSh = slide.Shapes.AddTextbox(msoTextOrientationHorizontal, Left:=leftPos - 4.057, Top:=topPos - 16.2, Width:=88.8204, Height:=17.60528)
With oSh
    .Name = "Data Heading (" & sHead & ")"
    With .TextFrame.TextRange
        .Text = sHead
        .ParagraphFormat.Alignment = ppAlignCenter
        With .Font
            .Name = "Nunito Sans"
            .Size = 8.12
            .Color = RGB(255, 255, 255)
        End With    ' Font
    End With        ' TextRange
End With            ' oSh, the shape itself
End If
End Sub

Public Sub CreateAlert(slide As PowerPoint.slide)
Dim oSh As PowerPoint.Shape

Set oSh = slide.Shapes.AddTextbox(msoTextOrientationHorizontal, Left:=308.1, Top:=385.4, Width:=448.75, Height:=30.9)
With oSh
    .Name = "Alert"
    .Fill.ForeColor.RGB = RGB(255, 192, 0)
    With .TextFrame.TextRange
        .Text = "Remember, figures are per role not per person" & vbNewLine & "(makes it better but not right!)"
        .ParagraphFormat.Alignment = ppAlignCenter
        With .Font
            .Name = "Nunito Sans"
            .Size = 9.75
        End With    ' Font
    End With        ' TextRange
End With            ' oSh, the shape itself

End Sub

Public Sub CopyImage(slide As PowerPoint.slide)

Dim logo As Object

wbMe.Sheets("Img").Shapes("logo").Copy

Set logo = slide.Shapes.PasteSpecial(ppPasteMetafilePicture, msoFalse)
With logo
    .Width = 126.6
    .Height = 120.11
    .Left = 625.42
    .Top = 10.2
End With
End Sub


Sub setupInfo(slide As PowerPoint.slide, sDataDate As String, sOrgName As String, lTotalAdults As Long, lTotalRoles As Long)
' create headers
CreateTextHeader slide, 98.6, 22.75, "The Basics Dashboard – " & sOrgName
CreateTextHeader slide, 485.9, 20, lTotalAdults & " Adults – " & lTotalRoles & " Roles"

' create legend
CreateLegend slide, 482.2, 82.97, "Data: " & sDataDate
CreateLegend slide, 500.71, 100.23, "Getting better"
CreateLegend slide, 500.71, 117.87, "Getting worse"

' create roles vs adults notice
CreateAlert slide

' copy image
CopyImage slide
End Sub
