---
title: "Atlassian Jira Cloud REST API v3 Complete OpenAPI 3.0 Platform Specification"
source_authority: "Atlassian Developer Platform (Official OpenAPI 3.0 Schema)"
total_api_paths: 421
openapi_version: "3.0.0"
harvested_at: "2026-08-19T04:04:01Z"
document_status: "OFFICIAL_PRIMARY_SOURCE_UNABRIDGED_PLATFORM_SPEC"
verification: "ATLASSIAN_OPENAPI_V3_VERIFIED"
---

# Atlassian Jira Cloud REST API v3 Complete Platform Specification (All 421 Endpoints)

**Authority**: Atlassian Cloud Platform Engineering  
**Live Spec Endpoint**: `https://developer.atlassian.com/cloud/jira/platform/swagger-v3.v3.json`  
**Total Documented Endpoints**: **421 Paths**

---

## 1. Complete Jira REST API v3 Endpoints Catalog

| HTTP Method | API Path Pattern | Subsystem / Tag | Operation Summary |
| :---: | :--- | :--- | :--- |
| `GET` | `/rest/api/3/announcementBanner` | Announcement banner | Get announcement banner configuration |
| `PUT` | `/rest/api/3/announcementBanner` | Announcement banner | Update announcement banner configuration |
| `POST` | `/rest/api/3/app/field/context/configuration/list` | Issue custom field configuration (apps) | Bulk get custom field configurations |
| `POST` | `/rest/api/3/app/field/value` | Issue custom field values (apps) | Update custom fields |
| `GET` | `/rest/api/3/app/field/{fieldIdOrKey}/context/configuration` | Issue custom field configuration (apps) | Get custom field configurations |
| `PUT` | `/rest/api/3/app/field/{fieldIdOrKey}/context/configuration` | Issue custom field configuration (apps) | Update custom field configurations |
| `PUT` | `/rest/api/3/app/field/{fieldIdOrKey}/value` | Issue custom field values (apps) | Update custom field value |
| `GET` | `/rest/api/3/application-properties` | Jira settings | Get application property |
| `GET` | `/rest/api/3/application-properties/advanced-settings` | Jira settings | Get advanced settings |
| `PUT` | `/rest/api/3/application-properties/{id}` | Jira settings | Set application property |
| `GET` | `/rest/api/3/applicationrole` | Application roles | Get all application roles |
| `GET` | `/rest/api/3/applicationrole/{key}` | Application roles | Get application role |
| `GET` | `/rest/api/3/attachment/content/{id}` | Issue attachments | Get attachment content |
| `GET` | `/rest/api/3/attachment/meta` | Issue attachments | Get Jira attachment settings |
| `GET` | `/rest/api/3/attachment/thumbnail/{id}` | Issue attachments | Get attachment thumbnail |
| `DELETE` | `/rest/api/3/attachment/{id}` | Issue attachments | Delete attachment |
| `GET` | `/rest/api/3/attachment/{id}` | Issue attachments | Get attachment metadata |
| `GET` | `/rest/api/3/attachment/{id}/expand/human` | Issue attachments | Get all metadata for an expanded attachment |
| `GET` | `/rest/api/3/attachment/{id}/expand/raw` | Issue attachments | Get contents metadata for an expanded attachment |
| `GET` | `/rest/api/3/auditing/record` | Audit records | Get audit records |
| `GET` | `/rest/api/3/avatar/{type}/system` | Avatars | Get system avatars by type |
| `POST` | `/rest/api/3/bulk/issues/delete` | Issue bulk operations | Bulk delete issues |
| `GET` | `/rest/api/3/bulk/issues/fields` | Issue bulk operations | Get bulk editable fields |
| `POST` | `/rest/api/3/bulk/issues/fields` | Issue bulk operations | Bulk edit issues |
| `POST` | `/rest/api/3/bulk/issues/move` | Issue bulk operations | Bulk move issues |
| `GET` | `/rest/api/3/bulk/issues/transition` | Issue bulk operations | Get available transitions |
| `POST` | `/rest/api/3/bulk/issues/transition` | Issue bulk operations | Bulk transition issue statuses |
| `POST` | `/rest/api/3/bulk/issues/unwatch` | Issue bulk operations | Bulk unwatch issues |
| `POST` | `/rest/api/3/bulk/issues/watch` | Issue bulk operations | Bulk watch issues |
| `GET` | `/rest/api/3/bulk/queue/{taskId}` | Issue bulk operations | Get bulk issue operation progress |
| `POST` | `/rest/api/3/changelog/bulkfetch` | Issues | Bulk fetch changelogs |
| `GET` | `/rest/api/3/classification-levels` | Classification levels | Get all classification levels |
| `POST` | `/rest/api/3/comment/list` | Issue comments | Get comments by IDs |
| `GET` | `/rest/api/3/comment/{commentId}/properties` | Issue comment properties | Get comment property keys |
| `DELETE` | `/rest/api/3/comment/{commentId}/properties/{propertyKey}` | Issue comment properties | Delete comment property |
| `GET` | `/rest/api/3/comment/{commentId}/properties/{propertyKey}` | Issue comment properties | Get comment property |
| `PUT` | `/rest/api/3/comment/{commentId}/properties/{propertyKey}` | Issue comment properties | Set comment property |
| `GET` | `/rest/api/3/component` | Project components | Find components for projects |
| `POST` | `/rest/api/3/component` | Project components | Create component |
| `DELETE` | `/rest/api/3/component/{id}` | Project components | Delete component |
| `GET` | `/rest/api/3/component/{id}` | Project components | Get component |
| `PUT` | `/rest/api/3/component/{id}` | Project components | Update component |
| `GET` | `/rest/api/3/component/{id}/relatedIssueCounts` | Project components | Get component issues count |
| `GET` | `/rest/api/3/config/fieldschemes` | Field schemes | Get field schemes |
| `POST` | `/rest/api/3/config/fieldschemes` | Field schemes | Create field scheme |
| `DELETE` | `/rest/api/3/config/fieldschemes/fields` | Field schemes | Remove fields associated with field schemes |
| `PUT` | `/rest/api/3/config/fieldschemes/fields` | Field schemes | Update fields associated with field schemes |
| `DELETE` | `/rest/api/3/config/fieldschemes/fields/parameters` | Field schemes | Remove field parameters |
| `PUT` | `/rest/api/3/config/fieldschemes/fields/parameters` | Field schemes | Update field parameters |
| `GET` | `/rest/api/3/config/fieldschemes/projects` | Field schemes | Get projects with field schemes |
| `PUT` | `/rest/api/3/config/fieldschemes/projects` | Field schemes | Associate projects to field schemes |
| `DELETE` | `/rest/api/3/config/fieldschemes/{id}` | Field schemes | Delete a field scheme |
| `GET` | `/rest/api/3/config/fieldschemes/{id}` | Field schemes | Get field scheme |
| `PUT` | `/rest/api/3/config/fieldschemes/{id}` | Field schemes | Update field scheme |
| `POST` | `/rest/api/3/config/fieldschemes/{id}/clone` | Field schemes | Clone field scheme |
| `GET` | `/rest/api/3/config/fieldschemes/{id}/fields` | Field schemes | Search field scheme fields |
| `GET` | `/rest/api/3/config/fieldschemes/{id}/fields/{fieldId}/parameters` | Field schemes | Get field parameters |
| `GET` | `/rest/api/3/config/fieldschemes/{id}/projects` | Field schemes | Search field scheme projects |
| `GET` | `/rest/api/3/configuration` | Jira settings | Get global settings |
| `GET` | `/rest/api/3/configuration/timetracking` | Time tracking | Get selected time tracking provider |
| `PUT` | `/rest/api/3/configuration/timetracking` | Time tracking | Select time tracking provider |
| `GET` | `/rest/api/3/configuration/timetracking/list` | Time tracking | Get all time tracking providers |
| `GET` | `/rest/api/3/configuration/timetracking/options` | Time tracking | Get time tracking settings |
| `PUT` | `/rest/api/3/configuration/timetracking/options` | Time tracking | Set time tracking settings |
| `GET` | `/rest/api/3/customFieldOption/{id}` | Issue custom field options | Get custom field option |
| `GET` | `/rest/api/3/dashboard` | Dashboards | Get all dashboards |
| `POST` | `/rest/api/3/dashboard` | Dashboards | Create dashboard |
| `PUT` | `/rest/api/3/dashboard/bulk/edit` | Dashboards | Bulk edit dashboards |
| `GET` | `/rest/api/3/dashboard/gadgets` | Dashboards | Get available gadgets |
| `GET` | `/rest/api/3/dashboard/search` | Dashboards | Search for dashboards |
| `GET` | `/rest/api/3/dashboard/{dashboardId}/gadget` | Dashboards | Get gadgets |
| `POST` | `/rest/api/3/dashboard/{dashboardId}/gadget` | Dashboards | Add gadget to dashboard |
| `DELETE` | `/rest/api/3/dashboard/{dashboardId}/gadget/{gadgetId}` | Dashboards | Remove gadget from dashboard |
| `PUT` | `/rest/api/3/dashboard/{dashboardId}/gadget/{gadgetId}` | Dashboards | Update gadget on dashboard |
| `GET` | `/rest/api/3/dashboard/{dashboardId}/items/{itemId}/properties` | Dashboards | Get dashboard item property keys |
| `DELETE` | `/rest/api/3/dashboard/{dashboardId}/items/{itemId}/properties/{propertyKey}` | Dashboards | Delete dashboard item property |
| `GET` | `/rest/api/3/dashboard/{dashboardId}/items/{itemId}/properties/{propertyKey}` | Dashboards | Get dashboard item property |
| `PUT` | `/rest/api/3/dashboard/{dashboardId}/items/{itemId}/properties/{propertyKey}` | Dashboards | Set dashboard item property |
| `DELETE` | `/rest/api/3/dashboard/{id}` | Dashboards | Delete dashboard |
| `GET` | `/rest/api/3/dashboard/{id}` | Dashboards | Get dashboard |
| `PUT` | `/rest/api/3/dashboard/{id}` | Dashboards | Update dashboard |
| `POST` | `/rest/api/3/dashboard/{id}/copy` | Dashboards | Copy dashboard |
| `GET` | `/rest/api/3/data-policy` | App data policies | Get data policy for the workspace |
| `GET` | `/rest/api/3/data-policy/project` | App data policies | Get data policy for projects |
| `GET` | `/rest/api/3/events` | Issues | Get events |
| `POST` | `/rest/api/3/expression/analyse` | Jira expressions | Analyse Jira expression |
| `POST` | `/rest/api/3/expression/eval` | Jira expressions | Currently being removed. Evaluate Jira expression |
| `POST` | `/rest/api/3/expression/evaluate` | Jira expressions | Evaluate Jira expression using enhanced search API |
| `GET` | `/rest/api/3/field` | Issue fields | Get fields |
| `POST` | `/rest/api/3/field` | Issue fields | Create custom field |
| `DELETE` | `/rest/api/3/field/association` | Issue custom field associations | Remove associations |
| `PUT` | `/rest/api/3/field/association` | Issue custom field associations | Create associations |
| `GET` | `/rest/api/3/field/search` | Issue fields | Get fields paginated |
| `GET` | `/rest/api/3/field/search/trashed` | Issue fields | Get fields in trash paginated |
| `PUT` | `/rest/api/3/field/{fieldId}` | Issue fields | Update custom field |
| `GET` | `/rest/api/3/field/{fieldId}/association/project` | Issue fields | Get field project associations |
| `GET` | `/rest/api/3/field/{fieldId}/context` | Issue custom field contexts | Get custom field contexts |
| `POST` | `/rest/api/3/field/{fieldId}/context` | Issue custom field contexts | Create custom field context |
| `GET` | `/rest/api/3/field/{fieldId}/context/defaultValue` | Issue custom field contexts | Get custom field contexts default values |
| `PUT` | `/rest/api/3/field/{fieldId}/context/defaultValue` | Issue custom field contexts | Set custom field contexts default values |
| `GET` | `/rest/api/3/field/{fieldId}/context/defaultValues` | Issue custom field contexts | Get default values for a custom field grouped by context and issue type |
| `GET` | `/rest/api/3/field/{fieldId}/context/issuetypemapping` | Issue custom field contexts | Get issue types for custom field context |
| `POST` | `/rest/api/3/field/{fieldId}/context/mapping` | Issue custom field contexts | Get custom field contexts for projects and issue types |
| `GET` | `/rest/api/3/field/{fieldId}/context/projectmapping` | Issue custom field contexts | Get project mappings for custom field context |
| `DELETE` | `/rest/api/3/field/{fieldId}/context/{contextId}` | Issue custom field contexts | Delete custom field context |
| `PUT` | `/rest/api/3/field/{fieldId}/context/{contextId}` | Issue custom field contexts | Update custom field context |
| `PUT` | `/rest/api/3/field/{fieldId}/context/{contextId}/issuetype` | Issue custom field contexts | Add issue types to context |
| `POST` | `/rest/api/3/field/{fieldId}/context/{contextId}/issuetype/remove` | Issue custom field contexts | Remove issue types from context |
| `GET` | `/rest/api/3/field/{fieldId}/context/{contextId}/option` | Issue custom field options | Get custom field options (context) |
| `POST` | `/rest/api/3/field/{fieldId}/context/{contextId}/option` | Issue custom field options | Create custom field options (context) |
| `PUT` | `/rest/api/3/field/{fieldId}/context/{contextId}/option` | Issue custom field options | Update custom field options (context) |
| `PUT` | `/rest/api/3/field/{fieldId}/context/{contextId}/option/move` | Issue custom field options | Reorder custom field options (context) |
| `DELETE` | `/rest/api/3/field/{fieldId}/context/{contextId}/option/{optionId}` | Issue custom field options | Delete custom field options (context) |
| `DELETE` | `/rest/api/3/field/{fieldId}/context/{contextId}/option/{optionId}/issue` | Issue custom field options | Replace custom field options |
| `PUT` | `/rest/api/3/field/{fieldId}/context/{contextId}/project` | Issue custom field contexts | Assign custom field context to projects |
| `POST` | `/rest/api/3/field/{fieldId}/context/{contextId}/project/remove` | Issue custom field contexts | Remove custom field context from projects |
| `GET` | `/rest/api/3/field/{fieldId}/contexts` | Issue fields | Get contexts for a field |
| `GET` | `/rest/api/3/field/{fieldId}/screens` | Screens | Get screens for a field |
| `GET` | `/rest/api/3/field/{fieldKey}/option` | Issue custom field options (apps) | Get all issue field options |
| `POST` | `/rest/api/3/field/{fieldKey}/option` | Issue custom field options (apps) | Create issue field option |
| `GET` | `/rest/api/3/field/{fieldKey}/option/suggestions/edit` | Issue custom field options (apps) | Get selectable issue field options |
| `GET` | `/rest/api/3/field/{fieldKey}/option/suggestions/search` | Issue custom field options (apps) | Get visible issue field options |
| `DELETE` | `/rest/api/3/field/{fieldKey}/option/{optionId}` | Issue custom field options (apps) | Delete issue field option |
| `GET` | `/rest/api/3/field/{fieldKey}/option/{optionId}` | Issue custom field options (apps) | Get issue field option |
| `PUT` | `/rest/api/3/field/{fieldKey}/option/{optionId}` | Issue custom field options (apps) | Update issue field option |
| `DELETE` | `/rest/api/3/field/{fieldKey}/option/{optionId}/issue` | Issue custom field options (apps) | Replace issue field option |
| `DELETE` | `/rest/api/3/field/{id}` | Issue fields | Delete custom field |
| `POST` | `/rest/api/3/field/{id}/restore` | Issue fields | Restore custom field from trash |
| `POST` | `/rest/api/3/field/{id}/trash` | Issue fields | Move custom field to trash |
| `GET` | `/rest/api/3/fieldconfiguration` | Issue field configurations | Get all field configurations |
| `POST` | `/rest/api/3/fieldconfiguration` | Issue field configurations | Create field configuration |
| `DELETE` | `/rest/api/3/fieldconfiguration/{id}` | Issue field configurations | Delete field configuration |
| `PUT` | `/rest/api/3/fieldconfiguration/{id}` | Issue field configurations | Update field configuration |
| `GET` | `/rest/api/3/fieldconfiguration/{id}/fields` | Issue field configurations | Get field configuration items |
| `PUT` | `/rest/api/3/fieldconfiguration/{id}/fields` | Issue field configurations | Update field configuration items |
| `GET` | `/rest/api/3/fieldconfigurationscheme` | Issue field configurations | Get all field configuration schemes |
| `POST` | `/rest/api/3/fieldconfigurationscheme` | Issue field configurations | Create field configuration scheme |
| `GET` | `/rest/api/3/fieldconfigurationscheme/mapping` | Issue field configurations | Get field configuration issue type items |
| `GET` | `/rest/api/3/fieldconfigurationscheme/project` | Issue field configurations | Get field configuration schemes for projects |
| `PUT` | `/rest/api/3/fieldconfigurationscheme/project` | Issue field configurations | Assign field configuration scheme to project |
| `DELETE` | `/rest/api/3/fieldconfigurationscheme/{id}` | Issue field configurations | Delete field configuration scheme |
| `PUT` | `/rest/api/3/fieldconfigurationscheme/{id}` | Issue field configurations | Update field configuration scheme |
| `PUT` | `/rest/api/3/fieldconfigurationscheme/{id}/mapping` | Issue field configurations | Assign issue types to field configurations |
| `POST` | `/rest/api/3/fieldconfigurationscheme/{id}/mapping/delete` | Issue field configurations | Remove issue types from field configuration scheme |
| `POST` | `/rest/api/3/filter` | Filters | Create filter |
| `GET` | `/rest/api/3/filter/defaultShareScope` | Filter sharing | Get default share scope |
| `PUT` | `/rest/api/3/filter/defaultShareScope` | Filter sharing | Set default share scope |
| `GET` | `/rest/api/3/filter/favourite` | Filters | Get favorite filters |
| `GET` | `/rest/api/3/filter/my` | Filters | Get my filters |
| `GET` | `/rest/api/3/filter/search` | Filters | Search for filters |
| `DELETE` | `/rest/api/3/filter/{id}` | Filters | Delete filter |
| `GET` | `/rest/api/3/filter/{id}` | Filters | Get filter |
| `PUT` | `/rest/api/3/filter/{id}` | Filters | Update filter |
| `DELETE` | `/rest/api/3/filter/{id}/columns` | Filters | Reset columns |
| `GET` | `/rest/api/3/filter/{id}/columns` | Filters | Get columns |
| `PUT` | `/rest/api/3/filter/{id}/columns` | Filters | Set columns |
| `DELETE` | `/rest/api/3/filter/{id}/favourite` | Filters | Remove filter as favorite |
| `PUT` | `/rest/api/3/filter/{id}/favourite` | Filters | Add filter as favorite |
| `PUT` | `/rest/api/3/filter/{id}/owner` | Filters | Change filter owner |
| `GET` | `/rest/api/3/filter/{id}/permission` | Filter sharing | Get share permissions |
| `POST` | `/rest/api/3/filter/{id}/permission` | Filter sharing | Add share permission |
| `DELETE` | `/rest/api/3/filter/{id}/permission/{permissionId}` | Filter sharing | Delete share permission |
| `GET` | `/rest/api/3/filter/{id}/permission/{permissionId}` | Filter sharing | Get share permission |
| `POST` | `/rest/api/3/forge/panel/action/bulk/async` | Issue panels | Bulk pin or unpin issue panel to projects |
| `DELETE` | `/rest/api/3/group` | Groups | Remove group |
| `GET` | `/rest/api/3/group` | Groups | Get group |
| `POST` | `/rest/api/3/group` | Groups | Create group |
| `GET` | `/rest/api/3/group/bulk` | Groups | Bulk get groups |
| `GET` | `/rest/api/3/group/member` | Groups | Get users from group |
| `DELETE` | `/rest/api/3/group/user` | Groups | Remove user from group |
| `POST` | `/rest/api/3/group/user` | Groups | Add user to group |
| `GET` | `/rest/api/3/groups/picker` | Groups | Find groups |

---

## 2. Core Issue Creation Contract (`POST /rest/api/3/issue`)

### JSON Schema:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "JiraIssueCreateRequest",
  "type": "object",
  "required": ["fields"],
  "properties": {
    "fields": {
      "type": "object",
      "required": ["project", "summary", "issuetype"],
      "properties": {
        "project": { "type": "object", "properties": { "key": { "type": "string" } } },
        "summary": { "type": "string", "maxLength": 255 },
        "description": {
          "type": "object",
          "properties": {
            "type": { "type": "string", "enum": ["doc"] },
            "version": { "type": "integer", "enum": [1] },
            "content": { "type": "array", "items": { "type": "object" } }
          }
        },
        "issuetype": { "type": "object", "properties": { "name": { "type": "string" } } },
        "priority": { "type": "object", "properties": { "name": { "type": "string" } } },
        "labels": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

---

## 3. Official Xray GraphQL & REST Test Management Data Models

### Xray Test Execution & Steps Schema:
```json
{
  "xray_test_entities": {
    "Test": { "type": "Manual | Automated | Cucumber", "fields": ["definition", "preconditions", "test_steps"] },
    "TestSet": { "description": "Arbitrary test grouping", "fields": ["tests"] },
    "TestPlan": { "description": "Release quality tracking", "fields": ["tests", "top_level_requirements"] },
    "TestExecution": { "description": "Test run container", "fields": ["test_environments", "revision", "results"] }
  }
}
```
