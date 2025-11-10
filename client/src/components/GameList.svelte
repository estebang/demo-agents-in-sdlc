<script lang="ts">
    import { onMount } from "svelte";

    interface Category {
        id: number;
        name: string;
    }

    interface Publisher {
        id: number;
        name: string;
    }

    interface Game {
        id: number;
        title: string;
        description: string;
        publisher?: Publisher;
        category?: Category;
        starRating?: number;
    }

    interface FilterOption {
        id: number;
        name: string;
        description?: string;
        game_count?: number;
    }

    export let games: Game[] = [];
    let loading = true;
    let error: string | null = null;
    let categories: FilterOption[] = [];
    let publishers: FilterOption[] = [];
    let selectedCategories: Set<number> = new Set();
    let selectedPublishers: Set<number> = new Set();
    let showFilters = false;

    const fetchCategories = async () => {
        try {
            const response = await fetch('/api/categories');
            if (response.ok) {
                categories = await response.json();
            }
        } catch (err) {
            console.error('Failed to fetch categories:', err);
        }
    };

    const fetchPublishers = async () => {
        try {
            const response = await fetch('/api/publishers');
            if (response.ok) {
                publishers = await response.json();
            }
        } catch (err) {
            console.error('Failed to fetch publishers:', err);
        }
    };

    const fetchGames = async () => {
        loading = true;
        try {
            // Build query string with filters
            const params = new URLSearchParams();
            selectedCategories.forEach(id => params.append('category_id', id.toString()));
            selectedPublishers.forEach(id => params.append('publisher_id', id.toString()));
            
            const queryString = params.toString();
            const url = queryString ? `/api/games?${queryString}` : '/api/games';
            
            const response = await fetch(url);
            if(response.ok) {
                games = await response.json();
            } else {
                error = `Failed to fetch data: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    const toggleCategory = (categoryId: number) => {
        if (selectedCategories.has(categoryId)) {
            selectedCategories.delete(categoryId);
        } else {
            selectedCategories.add(categoryId);
        }
        selectedCategories = selectedCategories; // Trigger reactivity
        fetchGames();
    };

    const togglePublisher = (publisherId: number) => {
        if (selectedPublishers.has(publisherId)) {
            selectedPublishers.delete(publisherId);
        } else {
            selectedPublishers.add(publisherId);
        }
        selectedPublishers = selectedPublishers; // Trigger reactivity
        fetchGames();
    };

    const clearFilters = () => {
        selectedCategories.clear();
        selectedPublishers.clear();
        selectedCategories = selectedCategories; // Trigger reactivity
        selectedPublishers = selectedPublishers; // Trigger reactivity
        fetchGames();
    };

    const hasActiveFilters = () => {
        return selectedCategories.size > 0 || selectedPublishers.size > 0;
    };

    onMount(() => {
        fetchCategories();
        fetchPublishers();
        fetchGames();
    });
</script>

<div>
    <div class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h2 class="text-2xl font-medium text-slate-100">Featured Games</h2>
        
        <button 
            on:click={() => showFilters = !showFilters}
            class="flex items-center gap-2 px-4 py-2 bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 rounded-lg transition-colors text-slate-200"
            data-testid="toggle-filters"
        >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z" clip-rule="evenodd" />
            </svg>
            <span>Filters</span>
            {#if hasActiveFilters()}
                <span class="px-2 py-0.5 text-xs bg-blue-600 text-white rounded-full">
                    {selectedCategories.size + selectedPublishers.size}
                </span>
            {/if}
        </button>
    </div>

    {#if showFilters}
        <div class="mb-6 p-4 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700" data-testid="filters-panel">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Categories Filter -->
                <div>
                    <h3 class="text-sm font-semibold text-slate-300 mb-3">Categories</h3>
                    <div class="space-y-2">
                        {#each categories as category}
                            <label class="flex items-center gap-2 cursor-pointer group">
                                <input 
                                    type="checkbox" 
                                    checked={selectedCategories.has(category.id)}
                                    on:change={() => toggleCategory(category.id)}
                                    class="w-4 h-4 rounded border-slate-600 bg-slate-700 text-blue-600 focus:ring-blue-500 focus:ring-offset-slate-900"
                                    data-testid="category-filter-{category.id}"
                                />
                                <span class="text-sm text-slate-300 group-hover:text-slate-100">
                                    {category.name}
                                    {#if category.game_count !== undefined}
                                        <span class="text-slate-500">({category.game_count})</span>
                                    {/if}
                                </span>
                            </label>
                        {/each}
                    </div>
                </div>

                <!-- Publishers Filter -->
                <div>
                    <h3 class="text-sm font-semibold text-slate-300 mb-3">Publishers</h3>
                    <div class="space-y-2">
                        {#each publishers as publisher}
                            <label class="flex items-center gap-2 cursor-pointer group">
                                <input 
                                    type="checkbox" 
                                    checked={selectedPublishers.has(publisher.id)}
                                    on:change={() => togglePublisher(publisher.id)}
                                    class="w-4 h-4 rounded border-slate-600 bg-slate-700 text-blue-600 focus:ring-blue-500 focus:ring-offset-slate-900"
                                    data-testid="publisher-filter-{publisher.id}"
                                />
                                <span class="text-sm text-slate-300 group-hover:text-slate-100">
                                    {publisher.name}
                                    {#if publisher.game_count !== undefined}
                                        <span class="text-slate-500">({publisher.game_count})</span>
                                    {/if}
                                </span>
                            </label>
                        {/each}
                    </div>
                </div>
            </div>

            {#if hasActiveFilters()}
                <div class="mt-4 pt-4 border-t border-slate-700">
                    <button 
                        on:click={clearFilters}
                        class="text-sm text-blue-400 hover:text-blue-300 transition-colors"
                        data-testid="clear-filters"
                    >
                        Clear all filters
                    </button>
                </div>
            {/if}
        </div>
    {/if}
    
    {#if loading}
        <!-- loading animation -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each Array(6) as _, i}
                <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50">
                    <div class="p-6">
                        <div class="animate-pulse">
                            <div class="h-6 bg-slate-700 rounded w-3/4 mb-3"></div>
                            <div class="h-4 bg-slate-700 rounded w-1/2 mb-4"></div>
                            <div class="h-3 bg-slate-700 rounded w-full mb-3"></div>
                            <div class="h-3 bg-slate-700 rounded w-5/6 mb-4"></div>
                            <div class="h-2 bg-slate-700 rounded-full w-full mb-2"></div>
                            <div class="h-4 bg-slate-700 rounded w-1/4 mt-4"></div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {:else if error}
        <!-- error display -->
        <div class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
            <p class="text-red-400">{error}</p>
        </div>
    {:else if games.length === 0}
        <!-- no games found -->
        <div class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
            <p class="text-slate-300">No games available at the moment.</p>
        </div>
    {:else}
        <!-- game list -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="games-grid">
            {#each games as game (game.id)}
                <a 
                    href={`/game/${game.id}`} 
                    class="group block bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50 hover:border-blue-500/50 hover:shadow-blue-500/10 hover:shadow-xl transition-all duration-300 hover:translate-y-[-6px]"
                    data-testid="game-card"
                    data-game-id={game.id}
                    data-game-title={game.title}
                >
                    <div class="p-6 relative">
                        <div class="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div class="relative z-10">
                            <h3 class="text-xl font-semibold text-slate-100 mb-2 group-hover:text-blue-400 transition-colors" data-testid="game-title">{game.title}</h3>
                            
                            {#if game.category || game.publisher}
                                <div class="flex gap-2 mb-3">
                                    {#if game.category}
                                        <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-blue-900/60 text-blue-300" data-testid="game-category">
                                            {game.category.name}
                                        </span>
                                    {/if}
                                    {#if game.publisher}
                                        <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-purple-900/60 text-purple-300" data-testid="game-publisher">
                                            {game.publisher.name}
                                        </span>
                                    {/if}
                                </div>
                            {/if}
                            
                            <p class="text-slate-400 mb-4 text-sm line-clamp-2" data-testid="game-description">{game.description}</p>
                            
                            <div class="mt-4 text-sm text-blue-400 font-medium flex items-center">
                                <span>View details</span>
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1 transform transition-transform duration-300 group-hover:translate-x-2" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                                </svg>
                            </div>
                        </div>
                    </div>
                </a>
            {/each}
        </div>
    {/if}
</div>