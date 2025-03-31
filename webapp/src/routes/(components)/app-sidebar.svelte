<script lang="ts">
  import Product from '@lucide/svelte/icons/package-search';
  import Shop from '@lucide/svelte/icons/store';
  import Task from '@lucide/svelte/icons/square-check-big';
  import History from '@lucide/svelte/icons/history';
  import Settings from '@lucide/svelte/icons/settings';
  import House from '@lucide/svelte/icons/house';
  import User from '@lucide/svelte/icons/user';
  import { ChevronDown, ChevronUp, ChevronRight } from '@lucide/svelte/icons';
  import * as Sidebar from '$lib/components/ui/sidebar';
  import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
  import * as Collapsible from '$lib/components/ui/collapsible';
  import { page } from '$app/state';

  const active_url = $derived(page.url.pathname);
  let {data} = $props();
  let workspace = $state('Taobao Analysis');
  // Menu items.
  const sidebar_items = [
    {
      group: true,
      title: 'Products',
      icon: Product,
      items: [
        {
          title: 'All Products',
          url: '/product'
        },
        {
          title: 'Product Detail',
          url: '/product/<product_id>'
        },
        {
          title: 'Product On Shelf',
          url: '/product/<product_id>/shelf'
        }
      ]
    },
    {
      group: true,
      title: 'Shops',
      icon: Shop,
      items: [
        {
          title: 'All Shops',
          url: '/shop'
        },
        {
          title: 'Shop Detail',
          url: '/shop/<shop_name>'
        }
      ]

    },
    {
      group: true,
      title: 'Tasks',
      icon: Task,
      items: [
        {
          title: 'All Tasks',
          url: '/task'
        },
        {
          title: 'Detail Crawl Tasks',
          url: '/task/detail'
        },
        {
          title: 'LLM Analyze Tasks',
          url: '/task/llm'
        },
        {
          title: 'Search Crawl Tasks',
          url: '/task/search'
        },
        {
          title: 'Shop Crawl Tasks',
          url: '/task/shop'
        },
        {
          title: 'Shop Search Crawl Tasks',
          url: '/task/shop_search'
        }
      ]
    },
    {
      group: false,
      title: 'Operation History',
      url: '/history',
      icon: History
    },
    {
      group: false,
      title: 'Management',
      url: '/management',
      icon: Settings
    }
  ];
  const valid_workspaces = [
    {
      title: 'Taobao Analysis',
      url: '/'
    }
  ];
</script>

<Sidebar.Root collapsible="icon">

    <!-- Header -->
    <Sidebar.Header>
        <Sidebar.Menu>
            <Sidebar.MenuItem>
                <DropdownMenu.Root>
                    <DropdownMenu.Trigger>
                        {#snippet child({props})}
                            <Sidebar.MenuButton {...props}>
                                <House/>
                                {workspace}
                                <ChevronDown class="ml-auto"/>
                            </Sidebar.MenuButton>
                        {/snippet}
                    </DropdownMenu.Trigger>
                    <DropdownMenu.Content class="w-[--bits-dropdown-menu-anchor-width]">
                        {#each valid_workspaces as valid_workspace (valid_workspace.title)}
                            <DropdownMenu.Item onclick={()=> workspace = valid_workspace.title}>
                                {#snippet child({props})}
                                    <a href={valid_workspace.url} {...props}>
                                        <span>{valid_workspace.title}</span>
                                    </a>
                                {/snippet}
                            </DropdownMenu.Item>
                        {/each}
                    </DropdownMenu.Content>
                </DropdownMenu.Root>
            </Sidebar.MenuItem>
        </Sidebar.Menu>
    </Sidebar.Header>

    <!-- Content -->
    <Sidebar.Content>
        <Sidebar.Group>
            <Sidebar.GroupContent>
                <Sidebar.Menu>
                    {#each sidebar_items as sidebar_item (sidebar_item.title)}
                        {#if sidebar_item.group}
                            <Collapsible.Root class="group/collapsible">
                                <Sidebar.MenuItem>
                                    <Collapsible.Trigger>
                                        {#snippet child({props})}
                                            <Sidebar.MenuButton {...props}>
                                                <sidebar_item.icon/>
                                                <span>{sidebar_item.title}</span>
                                                <ChevronRight class="ml-auto"/>
                                            </Sidebar.MenuButton>
                                        {/snippet}
                                    </Collapsible.Trigger>
                                    <Collapsible.Content>
                                        <Sidebar.MenuSub>
                                            {#if sidebar_item.items}
                                                {#each sidebar_item.items as item (item.title)}
                                                    <Sidebar.MenuSubItem>
                                                        <Sidebar.MenuSubButton isActive={active_url === item.url}>
                                                            {#snippet child({props})}
                                                                <a href={item.url} {...props}>
                                                                    <span>{item.title}</span>
                                                                </a>
                                                            {/snippet}
                                                        </Sidebar.MenuSubButton>
                                                    </Sidebar.MenuSubItem>
                                                {/each}
                                            {/if}
                                        </Sidebar.MenuSub>
                                    </Collapsible.Content>
                                </Sidebar.MenuItem>
                            </Collapsible.Root>
                        {:else}
                            <Sidebar.MenuItem>
                                <Sidebar.MenuButton isActive={active_url === sidebar_item.url}>
                                    {#snippet child({props})}
                                        <a href={sidebar_item.url} {...props}>
                                            <sidebar_item.icon/>
                                            <span>{sidebar_item.title}</span>
                                        </a>
                                    {/snippet}
                                </Sidebar.MenuButton>
                            </Sidebar.MenuItem>
                        {/if}
                    {/each}
                </Sidebar.Menu>
            </Sidebar.GroupContent>
        </Sidebar.Group>
    </Sidebar.Content>

    <!-- Footer -->
    <Sidebar.Footer>
        <Sidebar.Menu>
            <Sidebar.MenuItem>
                <DropdownMenu.Root>
                    <DropdownMenu.Trigger>
                        {#snippet child({props})}
                            <Sidebar.MenuButton
                                    {...props}
                                    class="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                            >
                                <User/>
                                {data.user.name}
                                <ChevronUp class="ml-auto"/>
                            </Sidebar.MenuButton>
                        {/snippet}
                    </DropdownMenu.Trigger>
                    <DropdownMenu.Content
                            class="w-[--bits-dropdown-menu-anchor-width]"
                            side="top"
                    >
                        <DropdownMenu.Item>
                            {#snippet child({props})}
                                <a href="/user/{data.user.id}" {...props}>
                                    <span>{data.user.name}</span>
                                </a>
                            {/snippet}
                        </DropdownMenu.Item>
                    </DropdownMenu.Content>
                </DropdownMenu.Root>
            </Sidebar.MenuItem>
        </Sidebar.Menu>
    </Sidebar.Footer>
</Sidebar.Root>