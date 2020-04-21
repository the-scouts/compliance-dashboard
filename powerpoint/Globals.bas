Attribute VB_Name = "Globals"
Option Explicit

Option Private Module

'============================================================================================
'
' Global constants and objects
'
'============================================================================================

' about us and used for settings

Global Const gsOURNAME                  As String = "Compliance Assistant"
Global Const gsSETUP                    As String = "Setup"

Global Const gsKeyFILECOMPLIANCE        As String = "Complaince Assistant File"
Global Const gsKeyFILETRAINING          As String = "Training Assistant File"
Global Const gsKeyDBSPCT                As String = "Percentage of valid disclosures"
Global Const gsKeyRPTTITLE              As String = "Report Title"

Global wbMe                             As Workbook
    
Global gdDataDisclosures                As Double
Global glDataFull                       As Long
Global glDataM01                        As Long
Global glDataM02                        As Long
Global glDataM034                       As Long
Global glDataGDPR                       As Long
Global glDataSfty                       As Long
Global glDataSafe                       As Long
Global glDataFA                         As Long
Global glDataWb                         As Long

Global glTotalAdults                    As Long
Global glTotalRoles                     As Long
Global gsDataDate                       As String
Global gsReportTitle                    As String

