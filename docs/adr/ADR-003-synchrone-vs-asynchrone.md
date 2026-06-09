# ADR-003 - Synchrone vs asynchrone

## Context
The initial implementation was developed using a synchronous approach, with six SmartPDUs defined in a JSON configuration file. After validating that the first version was working correctly, I considered adding more smart power distribution units. While extending the JSON file with additional SmartPDU definitions was possible, this approach appeared increasingly repetitive and less maintainable as the number of devices grew.

## Options considered
- Continue managing SmartPDUs through static JSON configuration.
- Refactor the application to use an asynchronous architecture.

## Decision
An asynchronous architecture was selected because it provides greater flexibility and scalability for future development. This approach simplifies the integration of additional SmartPDUs and other device types while improving the overall maintainability of the system.

## Reasons
Improved scalability of the application.
Easier integration of additional SmartPDUs and future device types.
Reduced configuration redundancy.
More efficient object creation and device management.
Better support for concurrent operations and future system growth.

## Status 
✅ Implemented