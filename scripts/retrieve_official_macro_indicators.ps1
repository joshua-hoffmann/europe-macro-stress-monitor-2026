Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RegistryPath = Join-Path $ProjectRoot "data/source_registry.csv"
$SchemaPath = Join-Path $ProjectRoot "data/official_macro_indicators_schema.csv"
$OutputPath = Join-Path $ProjectRoot "data/official_macro_indicators.csv"

$AllowedDatasets = @("nama_10_gdp", "prc_hicp_aind", "une_rt_m", "gov_10dd_edpt1")
$Registry = Import-Csv -LiteralPath $RegistryPath
$RegistryById = @{}
foreach ($Row in $Registry) {
    $RegistryById[$Row.source_id] = $Row
}

$SchemaHeader = (Get-Content -LiteralPath $SchemaPath -TotalCount 1).Split(",")
$RetrievedAt = [DateTimeOffset]::Now.ToString("o")

$Geographies = @("AT", "EU27_2020")

$Specs = @(
    [ordered]@{
        SourceId = "eurostat_gdp_annual_growth_real"
        Dataset = "nama_10_gdp"
        Query = @{ freq = "A"; na_item = "B1GQ"; unit = "CLV_PCH_PRE" }
        ComparabilityGroup = "annual_real_gdp_growth"
        DefinitionNote = "Annual real GDP growth; chain linked volumes; percentage change on previous period."
    },
    [ordered]@{
        SourceId = "eurostat_hicp_annual_all_items"
        Dataset = "prc_hicp_aind"
        Query = @{ freq = "A"; coicop = "CP00"; unit = "RCH_A_AVG" }
        ComparabilityGroup = "annual_hicp_all_items"
        DefinitionNote = "Annual all-items HICP inflation; annual average rate of change."
    },
    [ordered]@{
        SourceId = "eurostat_hicp_annual_energy"
        Dataset = "prc_hicp_aind"
        Query = @{ freq = "A"; coicop = "NRG"; unit = "RCH_A_AVG" }
        ComparabilityGroup = "annual_hicp_energy"
        DefinitionNote = "Annual HICP energy inflation; annual average rate of change. This is not a broad energy stress proxy."
    },
    [ordered]@{
        SourceId = "eurostat_unemployment_monthly_rate"
        Dataset = "une_rt_m"
        Query = @{ freq = "M"; age = "TOTAL"; sex = "T"; unit = "PC_ACT"; s_adj = "SA" }
        ComparabilityGroup = "monthly_unemployment_frequency_mismatch"
        DefinitionNote = "Monthly unemployment rate; total age aggregate; percentage of labour force; seasonally adjusted. Frequency differs from annual MVP indicators."
    },
    [ordered]@{
        SourceId = "eurostat_government_debt_gross"
        Dataset = "gov_10dd_edpt1"
        Query = @{ freq = "A"; sector = "S13"; na_item = "GD"; unit = "PC_GDP" }
        ComparabilityGroup = "annual_government_finance"
        DefinitionNote = "General government consolidated gross debt; percentage of GDP."
    },
    [ordered]@{
        SourceId = "eurostat_government_balance_b9"
        Dataset = "gov_10dd_edpt1"
        Query = @{ freq = "A"; sector = "S13"; na_item = "B9"; unit = "PC_GDP" }
        ComparabilityGroup = "annual_government_finance"
        DefinitionNote = "General government net lending (+) or net borrowing (-); percentage of GDP. Preserve sign and definition."
    }
)

function New-EurostatUri {
    param(
        [string]$Dataset,
        [hashtable]$Query
    )

    $Parameters = [ordered]@{
        lang = "en"
        format = "JSON"
    }
    foreach ($Key in ($Query.Keys | Sort-Object)) {
        $Parameters[$Key] = $Query[$Key]
    }

    $Pairs = foreach ($Key in $Parameters.Keys) {
        "{0}={1}" -f $Key, [uri]::EscapeDataString([string]$Parameters[$Key])
    }

    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/${Dataset}?$($Pairs -join "&")"
}

function Get-DimensionLabel {
    param(
        [pscustomobject]$Response,
        [string]$Dimension,
        [string]$Code
    )

    $DimProperty = $Response.dimension.PSObject.Properties[$Dimension]
    if (-not $DimProperty) {
        return $Code
    }

    $LabelContainer = $DimProperty.Value.category.label
    if (-not $LabelContainer) {
        return $Code
    }

    $LabelProperty = $LabelContainer.PSObject.Properties[$Code]
    if (-not $LabelProperty) {
        return $Code
    }

    [string]$LabelProperty.Value
}

function Convert-ValueToInvariantString {
    param($Value)

    if ($null -eq $Value) {
        return ""
    }

    if ($Value -is [double] -or $Value -is [single] -or $Value -is [decimal] -or $Value -is [int] -or $Value -is [long]) {
        return [Convert]::ToString($Value, [Globalization.CultureInfo]::InvariantCulture)
    }

    [string]$Value
}

function Get-PeriodBounds {
    param(
        [string]$TimePeriod,
        [string]$Frequency
    )

    if ($Frequency -eq "Annual" -and $TimePeriod -match "^\d{4}$") {
        return @{
            Start = "$TimePeriod-01-01"
            End = "$TimePeriod-12-31"
        }
    }

    if ($Frequency -eq "Monthly" -and $TimePeriod -match "^(\d{4})-(\d{2})$") {
        $Year = [int]$Matches[1]
        $Month = [int]$Matches[2]
        $Start = Get-Date -Year $Year -Month $Month -Day 1
        $End = $Start.AddMonths(1).AddDays(-1)
        return @{
            Start = $Start.ToString("yyyy-MM-dd")
            End = $End.ToString("yyyy-MM-dd")
        }
    }

    @{
        Start = ""
        End = ""
    }
}

function Get-LatestObservation {
    param(
        [string]$Dataset,
        [hashtable]$Query
    )

    $Uri = New-EurostatUri -Dataset $Dataset -Query $Query
    $Response = Invoke-RestMethod -Uri $Uri

    $Ids = @($Response.id)
    $Sizes = @($Response.size)

    if ($Ids -notcontains "time") {
        return @{
            Status = "gap"
            Reason = "response has no time dimension"
            Uri = $Uri
        }
    }

    for ($Index = 0; $Index -lt $Ids.Count; $Index++) {
        if ([int]$Sizes[$Index] -eq 0) {
            return @{
                Status = "gap"
                Reason = "dimension $($Ids[$Index]) has zero categories for requested filters"
                Uri = $Uri
            }
        }

        if ($Ids[$Index] -ne "time" -and [int]$Sizes[$Index] -gt 1) {
            return @{
                Status = "gap"
                Reason = "dimension $($Ids[$Index]) has multiple categories after filtering"
                Uri = $Uri
            }
        }
    }

    if (-not $Response.value) {
        return @{
            Status = "gap"
            Reason = "response has no numeric value object"
            Uri = $Uri
        }
    }

    $Values = @{}
    foreach ($Property in $Response.value.PSObject.Properties) {
        $Values[[int]$Property.Name] = $Property.Value
    }

    $TimeIndexes = $Response.dimension.time.category.index.PSObject.Properties | ForEach-Object {
        [pscustomobject]@{
            Time = $_.Name
            Index = [int]$_.Value
        }
    }

    foreach ($TimeIndex in ($TimeIndexes | Sort-Object Index -Descending)) {
        if ($Values.ContainsKey($TimeIndex.Index) -and $null -ne $Values[$TimeIndex.Index]) {
            return @{
                Status = "ok"
                Response = $Response
                Time = $TimeIndex.Time
                Value = $Values[$TimeIndex.Index]
                Uri = $Uri
            }
        }
    }

    @{
        Status = "gap"
        Reason = "no non-blank numeric value found for returned time periods"
        Uri = $Uri
    }
}

$OutputRows = New-Object System.Collections.Generic.List[object]
$Gaps = New-Object System.Collections.Generic.List[object]

foreach ($Spec in $Specs) {
    if ($AllowedDatasets -notcontains $Spec.Dataset) {
        throw "Dataset $($Spec.Dataset) is outside the approved retrieval scope."
    }

    if (-not $RegistryById.ContainsKey($Spec.SourceId)) {
        throw "source_id $($Spec.SourceId) is missing from source_registry.csv."
    }

    $RegistryRow = $RegistryById[$Spec.SourceId]
    if ($RegistryRow.validation_status -ne "validated") {
        throw "source_id $($Spec.SourceId) is not marked validated in source_registry.csv."
    }

    foreach ($GeoCode in $Geographies) {
        $Query = @{}
        foreach ($Key in $Spec.Query.Keys) {
            $Query[$Key] = $Spec.Query[$Key]
        }
        $Query["geo"] = $GeoCode

        $Latest = Get-LatestObservation -Dataset $Spec.Dataset -Query $Query

        if ($Latest.Status -ne "ok") {
            $Gaps.Add([pscustomobject]@{
                source_id = $Spec.SourceId
                dataset_code = $Spec.Dataset
                geo_code = $GeoCode
                reason = $Latest.Reason
                uri = $Latest.Uri
            })
            continue
        }

        $Response = $Latest.Response
        $Frequency = if ($Query["freq"] -eq "A") { "Annual" } elseif ($Query["freq"] -eq "M") { "Monthly" } else { $Query["freq"] }
        $Bounds = Get-PeriodBounds -TimePeriod $Latest.Time -Frequency $Frequency
        $GeoLabel = Get-DimensionLabel -Response $Response -Dimension "geo" -Code $GeoCode
        $ObservationId = ("{0}_{1}_{2}" -f $Spec.SourceId, $GeoCode, $Latest.Time) -replace "[^A-Za-z0-9_]", "_"

        $OutputRows.Add([ordered]@{
            observation_id = $ObservationId
            source_id = $Spec.SourceId
            source_institution = $RegistryRow.source_institution
            dataset_code = $Spec.Dataset
            indicator_code = $RegistryRow.indicator_code
            indicator_name_project = $RegistryRow.indicator_name_project
            indicator_name_source = $RegistryRow.indicator_name_source
            geo_code = $GeoCode
            geo_label = $GeoLabel
            time_period = $Latest.Time
            period_start = $Bounds.Start
            period_end = $Bounds.End
            frequency = $Frequency
            value = Convert-ValueToInvariantString -Value $Latest.Value
            unit = $RegistryRow.unit
            scale = "source value as reported"
            seasonal_adjustment = $RegistryRow.seasonal_adjustment
            observation_type = "Observation"
            latest_available_flag = "TRUE"
            retrieved_at = $RetrievedAt
            source_release_date = $Response.updated
            revision_status = "not_assessed"
            comparability_group = $Spec.ComparabilityGroup
            definition_note = $Spec.DefinitionNote
            quality_flag = "validated_live_retrieval"
            include_in_public_mvp = "TRUE"
        })
    }
}

$CsvRows = foreach ($Row in $OutputRows) {
    $Ordered = [ordered]@{}
    foreach ($Column in $SchemaHeader) {
        $Ordered[$Column] = $Row[$Column]
    }
    [pscustomobject]$Ordered
}

$CsvRows | Export-Csv -LiteralPath $OutputPath -NoTypeInformation

[pscustomobject]@{
    output_path = $OutputPath
    rows_written = $CsvRows.Count
    gaps = $Gaps.Count
    retrieved_at = $RetrievedAt
}

if ($Gaps.Count -gt 0) {
    $Gaps | Format-Table -AutoSize
}
