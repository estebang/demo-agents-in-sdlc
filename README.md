# Tailspin Toys

This repository contains the project for a 1 hour guided workshop to explore GitHub Copilot Agent Mode and related features in Visual Studio Code. The project is a website for a fictional game crowd-funding company, with a [Flask](https://flask.palletsprojects.com/en/stable/) backend using [SQLAlchemy](https://www.sqlalchemy.org/) and [Astro](https://astro.build/) frontend using [Svelte](https://svelte.dev/) for dynamic pages.

## Start the workshop

**To begin the workshop, start at [docs/README.md](./docs/README.md)**

Or, if just want to run the app...

## Launch the site

A script file has been created to launch the site. You can run it by:

```bash
./scripts/start-app.sh
```

Then navigate to the [website](http://localhost:4321) to see the site!

## Features

### Game Filtering

Users can filter games by category and publisher to find games that match their interests:

- Click the "Filters" button to open the filter panel
- Select one or more categories (Strategy, Puzzle, Simulation, Adventure, Action)
- Select one or more publishers (CodeForge Studios, DevMasters Inc., GitHub Games, Ops Interactive)
- Filters update the game list dynamically without page reload
- Click "Clear all filters" to reset the view

The filtering is powered by:
- Backend API endpoints: `/api/games?category_id=1&publisher_id=2`
- Frontend Svelte component with reactive filtering
- RESTful API design supporting multiple filter values

## License 

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./LICENSE) for the full terms.

## Maintainers 

You can find the list of maintainers in [CODEOWNERS](./.github/CODEOWNERS).

## Support

This project is provided as-is, and may be updated over time. If you have questions, please open an issue.
