# AI Response Generation Mandate

**Primary Directive:** All future responses, without exception, must be generated based *exclusively* on the information and specifications contained within the `docs` folder of this project. Read all files in the docs folder and base all responses on that documentation. Do not introduce external information, alternative technologies, or deviate from the documented project scope. The docs folder is the single source of truth.

**Data Generation Rule:** Never generate hardcoded data, mock data, or sample data. All data must come from real sources or be dynamically generated through proper data collection mechanisms.

**UI Loading State Rule:** When API data is not available or loading, always display skeleton loading components instead of mock/placeholder data. Never show fake content while waiting for real data.
