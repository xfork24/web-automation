<script lang="ts">
  import * as Breadcrumb from '$lib/components/ui/breadcrumb';
  import * as Dialog from '$lib/components/ui/dialog';
  import * as Sidebar from '$lib/components/ui/sidebar';
  import * as Popover from "$lib/components/ui/popover/index.js";
  import * as Tooltip from "$lib/components/ui/tooltip/index.js";
  import { Label } from "$lib/components/ui/label";
  import { Input } from "$lib/components/ui/input";
  import { Button } from "$lib/components/ui/button";
  import { Toaster } from "$lib/components/ui/sonner";
  import { toast } from "svelte-sonner";
  import { invalidateAll } from "$app/navigation";
  import HistoryDataTable from "./(components)/history-data-table.svelte";
  import {
    PLATFORM_REDNOTE,
    PLATFORM_TAOBAO, SHADOW_OPERATION_ONSHELF,
    SHADOW_STATUS_READY
  } from "../../../(components)/model";
  import { Tally1 } from "@lucide/svelte";
  import { Separator } from "$lib/components/ui/separator";

  let {data} = $props();

  const product_id = data.product_id!;
  const histories = data.shadow_histories;

  let product_title = $state(data.shadow_info.product_title);
  let product_price = $state(data.shadow_info.price)
  let product_inventory = $state(data.shadow_info.inventory);
  let title_imgs = $state(data.shadow_info.title_imgs);
  let page_imgs = $state(data.shadow_info.page_imgs);
  let offer_details = $state(data.shadow_info.offer_details);
  let additional_properties = $state(data.shadow_info.additional_properties);
  let new_title_imgs: string[] = $state([]);
  let new_page_imgs: string[] = $state([]);

  let open = $state(false);
  let dialog_title = $state('Are you sure?');
  let dialog_body = $state('');
  let handler = $state(async function () {
  });

  function onRemoveImage(target: string, img: string) {
    if (target == 'title') {
      title_imgs = title_imgs.filter((i: string) => i != img);
    } else if (target == 'page') {
      page_imgs = page_imgs.filter((i: string) => i != img);
    }
  }

  function onAddImages(target: string, e: Event) {
    Array.from((e.target as HTMLInputElement).files!).forEach(f => {
      if (target == 'title') {
        new_title_imgs.push(URL.createObjectURL(f));
      } else if (target == 'page') {
        new_page_imgs.push(URL.createObjectURL(f));
      }
    });
  }

  async function onSubmitImages(product_id: string, endpoint: string, e: Event) {
    e.preventDefault();
    const fileInput = document.getElementById(endpoint)! as HTMLInputElement;
    const url = `http://localhost:8000/api/v1/shadow_product/${product_id}/upload/${endpoint}?update_id={data.user.name}`;
    const selectedFiles = fileInput.files!;
    if (selectedFiles.length === 0) {
      toast("Please select at least one image to upload.");
      return;
    }
    const formData = new FormData();
    Array.from(selectedFiles as FileList).forEach(f => {
      formData.append(endpoint, f);
    })

    const xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.onreadystatechange = async function () {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status === 200) {
          // Handle successful response from the server
          await invalidateAll();
          title_imgs = data.shadow_info.title_imgs;
          page_imgs = data.shadow_info.page_imgs;
          new_title_imgs = [];
          new_page_imgs = [];
          fileInput.value = "";
          toast("Submit Successful");
        } else {
          // Handle error response from the server
          await invalidateAll();
          toast("Submit Failed");
        }
      }
    };
    xhr.send(formData);
  }

  function onResetProductDialog() {
    dialog_body = 'This action will reset product information.';
    handler = onResetProduct;
  }

  function onSaveProductDialog() {
    dialog_body = 'This action will save product information.';
    handler = onSaveProduct;
  }

  function onShelfTaobaoDialog() {
    dialog_body = 'This action will onshelf this product to Taobao. The task will be scheduled later.';
    handler = onShelfTaobao;
  }

  function onShelfRednoteDialog() {
    dialog_body = 'This action will onshelf this product to Rednote. The task will be scheduled later.';
    handler = onShelfRednote;
  }

  async function onResetProduct() {
    open = false;
    await invalidateAll();
    product_title = data.shadow_info.product_title;
    product_price = data.shadow_info.price;
    product_inventory = data.shadow_info.inventory;
    title_imgs = data.shadow_info.title_imgs;
    page_imgs = data.shadow_info.page_imgs;
    offer_details = data.shadow_info.offer_details;
    additional_properties = data.shadow_info.additional_properties;
    new_title_imgs = [];
    new_page_imgs = [];
    toast("Information Reset Successful");
  }

  async function onSaveProduct() {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/shadow_product/${product_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        },
        body: JSON.stringify({
          'status': SHADOW_STATUS_READY,
          'update_id': data.user.name,
          'product_title': product_title,
          'shop_name': data.shadow_info.shop_name,
          'price': product_price,
          'inventory': product_inventory,
          'title_imgs': title_imgs,
          'page_imgs': page_imgs,
          'offer_details': data.shadow_info.offer_details,
          'additional_properties': data.shadow_info.additional_properties,
        })
      });
      const result = await response.json();
      if (result.code == 0) {
        open = false;
        await invalidateAll();
        toast("Operation Successful");
      }
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

  async function onShelfTaobao() {
    try {
      if (data.shadow_info.status !== SHADOW_STATUS_READY) {
        open = false;
        await invalidateAll();
        toast("Operation Failed: Product must be in READY status.");
        return;
      }
      data.shadow_info.additional_properties.platform_mask |= PLATFORM_TAOBAO;
      const save_response = await fetch(`http://localhost:8000/api/v1/shadow_product/${product_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        },
        body: JSON.stringify({
          'status': SHADOW_STATUS_READY,
          'update_id': data.user.name,
          'product_title': product_title,
          'shop_name': data.shadow_info.shop_name,
          'price': product_price,
          'inventory': product_inventory,
          'title_imgs': title_imgs,
          'page_imgs': page_imgs,
          'offer_details': data.shadow_info.offer_details,
          'additional_properties': data.shadow_info.additional_properties,
        })
      });
      const save_result = await save_response.json();
      if (save_result.code == 0) {
        const task_response = await fetch('http://localhost:8000/api/v1/product_task', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json;charset=UTF-8'
          },
          body: JSON.stringify({
            'product_id': product_id,
            'shop_name': '归去来宝藏店',
            'platform': PLATFORM_TAOBAO,
            'operation': SHADOW_OPERATION_ONSHELF,
            'update_id': data.user.name
          })
        });
        const task_result = await task_response.json();
        if (task_result.code == 0) {
          open = false;
          await invalidateAll();
          toast("Operation Successful");
        }
      }
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }

  async function onShelfRednote() {
    try {
      if (data.shadow_info.status !== SHADOW_STATUS_READY) {
        open = false;
        await invalidateAll();
        toast("Operation Failed: Product must be in READY status.");
        return;
      }
      data.shadow_info.additional_properties.platform_mask |= PLATFORM_REDNOTE;
      const save_response = await fetch(`http://localhost:8000/api/v1/shadow_product/${product_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        },
        body: JSON.stringify({
          'status': SHADOW_STATUS_READY,
          'update_id': data.user.name,
          'product_title': product_title,
          'shop_name': data.shadow_info.shop_name,
          'price': product_price,
          'inventory': product_inventory,
          'title_imgs': title_imgs,
          'page_imgs': page_imgs,
          'offer_details': data.shadow_info.offer_details,
          'additional_properties': data.shadow_info.additional_properties,
        })
      });
      const save_result = await save_response.json();
      if (save_result.code == 0) {
        const task_response = await fetch('http://localhost:8000/api/v1/product_task', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json;charset=UTF-8'
          },
          body: JSON.stringify({
            'product_id': product_id,
            'shop_name': '归去来兮薯的店',
            'platform': PLATFORM_REDNOTE,
            'operation': SHADOW_OPERATION_ONSHELF,
            'update_id': data.user.name
          })
        });
        const task_result = await task_response.json();
        if (task_result.code == 0) {
          open = false;
          await invalidateAll();
          toast("Operation Successful");
        }
      }
    } catch (error) {
      console.error(`Error in function: ${error}`);
    }
  }
</script>

<Toaster/>

<Sidebar.Inset>
  <header class="flex h-16 shrink-0 items-center gap-2">
    <div class="flex items-center gap-2 px-4">
      <Sidebar.Trigger/>
      <Breadcrumb.Root>
        <Breadcrumb.List>
          <Breadcrumb.Separator>
            <Tally1/>
          </Breadcrumb.Separator>
          <Breadcrumb.Item>
            <Breadcrumb.Link href="/static">Home</Breadcrumb.Link>
          </Breadcrumb.Item>
          <Breadcrumb.Separator/>
          <Breadcrumb.Item>
            <Breadcrumb.Link href="/product">Products</Breadcrumb.Link>
          </Breadcrumb.Item>
          <Breadcrumb.Separator/>
          <Breadcrumb.Item>
            <Breadcrumb.Link href="/shadow/{product_id}/shelf">Product On Shelf</Breadcrumb.Link>
          </Breadcrumb.Item>
        </Breadcrumb.List>
      </Breadcrumb.Root>
    </div>
  </header>
  <main>
    {#if data.shadow_info !== undefined && data.shadow_info.status !== 0}
      <div class="items-center justify-between px-4 text-4xl">Product OnShelf</div>
      <div class="flex flex-col gap-2">
        <div class="flex flex-nowrap px-4 w-full items-center">
          <div class="w-1/6">
            <Label>Product Title: </Label>
          </div>
          <div class="w-5/6">
            <Input id="title" value={product_title}
                   oninput={(e) => product_title = e.currentTarget.value}/>
          </div>
        </div>
        <div class="flex flex-nowrap px-4 w-full items-center">
          <div class="w-1/6">
            <Label>Price: </Label>
          </div>
          <div class="w-5/6">
            <Input id="price" value={product_price / 100}
                   oninput={(e) => product_price = Number.parseFloat(e.currentTarget.value) * 100}/>
          </div>
        </div>
        <div class="flex flex-nowrap px-4 w-full items-center">
          <div class="w-1/6">
            <Label>Inventory: </Label>
          </div>
          <div class="w-5/6">
            <Input id="inventory" value={product_inventory}
                   oninput={(e) => product_inventory = Number.parseFloat(e.currentTarget.value)}/>
          </div>
        </div>
        <div class="flex px-4 w-full items-center">
          <div class="w-1/6">
            <Label>Title Images: </Label>
          </div>
          <div class="flex flex-wrap gap-4 w-5/6">
            {#each title_imgs as title_img (title_img)}
              <Popover.Root>
                <Popover.Trigger>
                  <img class="h-32 w-32 object-scale-down mr-2"
                       src={data.shadow_info.additional_properties.resource_root + '/title_images/' + title_img}
                       alt={title_img}/>
                </Popover.Trigger>
                <Popover.Content class="w-30">
                  <div class="flex flex-col items-center gap-4">
                    <div>
                      <Button variant="outline" onclick={() => onRemoveImage('title', title_img)}>Remove</Button>
                    </div>
                  </div>
                </Popover.Content>
              </Popover.Root>
            {/each}
            <Separator orientation="vertical"/>
            {#each new_title_imgs as new_title_img (new_title_img)}
              <img class="h-32 w-32 object-scale-down mr-2" src={new_title_img} alt={new_title_img}/>
            {/each}
            <div class="flex flex-wrap items-center gap-4">
              <form method="POST" enctype="multipart/form-data"
                    onsubmit={(e) => onSubmitImages(product_id, 'title_images_upload', e)}>
                <input type="file" id="title_images_upload" class="block py-2 w-full text-sm text-slate-500
                       file:mr-4 file:py-2 file:px-4 file:rounded-full
                       file:border-0 file:text-sm file:font-semibold
                       file:bg-violet-50 file:text-violet-700
                       hover:file:bg-violet-100 button" multiple onchange={(e) => onAddImages('title', e)}
                       accept="image/jpeg,image/jpg,image/png"/>
                <button type="submit" class="block text-sm mr-4 py-2 px-4 rounded-full font-semibold
                text-violet-700 bg-violet-50 hover:bg-violet-100">Submit
                </button>
              </form>
            </div>
          </div>
        </div>
        <div class="flex px-4 items-center">
          <div class="w-1/6">
            <Label>Page Images: </Label>
          </div>
          <div class="flex flex-wrap gap-4 w-5/6">
            {#each page_imgs as page_img (page_img)}
              <Popover.Root>
                <Popover.Trigger>
                  <img class="h-32 w-32 object-scale-down mr-2"
                       src={data.shadow_info.additional_properties.resource_root + '/page_images/' + page_img}
                       alt={page_img}/>
                </Popover.Trigger>
                <Popover.Content class="w-30">
                  <div class="flex flex-col items-center gap-4">
                    <div>
                      <Button variant="outline" onclick={() => onRemoveImage('page', page_img)}>Remove</Button>
                    </div>
                  </div>
                </Popover.Content>
              </Popover.Root>
            {/each}
            <Separator orientation="vertical"/>
            {#each new_page_imgs as new_page_img (new_page_img)}
              <img class="h-32 w-32 object-scale-down mr-2" src={new_page_img} alt={new_page_img}/>
            {/each}
            <div class="flex flex-wrap items-center gap-4">
              <form method="POST" enctype="multipart/form-data"
                    onsubmit={(e) => onSubmitImages(product_id, 'page_images_upload', e)}>
                <input type="file" id="page_images_upload" class="block py-2 w-full text-sm text-slate-500
                       file:mr-4 file:py-2 file:px-4 file:rounded-full
                       file:border-0 file:text-sm file:font-semibold
                       file:bg-violet-50 file:text-violet-700
                       hover:file:bg-violet-100 button" multiple onchange={(e) => onAddImages('page', e)}
                       accept="image/jpeg,image/jpg,image/png"/>
                <button type="submit" class="block text-sm mr-4 py-2 px-4 rounded-full font-semibold
                text-violet-700 bg-violet-50 hover:bg-violet-100">Submit
                </button>
              </form>
            </div>
          </div>
        </div>
        <div class="flex flex-nowrap px-4 w-full items-center">
          <div class="w-1/6">
            <Label>Resource Root: </Label>
          </div>
          <div class="w-5/6">
            <Label>{data.shadow_info.additional_properties.resource_root}</Label>
          </div>
        </div>
        <Dialog.Root bind:open>
          <div class="flex flex-row gap-4 p-4 items-center justify-end">
            <Dialog.Trigger class="mr-4">
              <Tooltip.Provider>
                <Tooltip.Root>
                  <Tooltip.Trigger>
                    <Dialog.Trigger>
                      <Button variant="destructive" onclick={() => onResetProductDialog()}>Reset</Button>
                    </Dialog.Trigger>
                  </Tooltip.Trigger>
                  <Tooltip.Content>
                    <p>Reset to original product information</p>
                  </Tooltip.Content>
                </Tooltip.Root>
              </Tooltip.Provider>
            </Dialog.Trigger>

            <Dialog.Trigger class="mr-4">
              <Tooltip.Provider>
                <Tooltip.Root>
                  <Tooltip.Trigger>
                    <Dialog.Trigger>
                      <Button variant="destructive" onclick={() => onSaveProductDialog()}>Save</Button>
                    </Dialog.Trigger>
                  </Tooltip.Trigger>
                  <Tooltip.Content>
                    <p>Save product information</p>
                  </Tooltip.Content>
                </Tooltip.Root>
              </Tooltip.Provider>
            </Dialog.Trigger>

            <Dialog.Trigger class="mr-4">
              <Tooltip.Provider>
                <Tooltip.Root>
                  <Tooltip.Trigger>
                    <Dialog.Trigger>
                      <Button variant="destructive" onclick={() => onShelfTaobaoDialog()}>Onshelf Taobao</Button>
                    </Dialog.Trigger>
                  </Tooltip.Trigger>
                  <Tooltip.Content>
                    <p>Onshelf product to Taobao</p>
                  </Tooltip.Content>
                </Tooltip.Root>
              </Tooltip.Provider>
            </Dialog.Trigger>

            <Dialog.Trigger class="mr-4">
              <Tooltip.Provider>
                <Tooltip.Root>
                  <Tooltip.Trigger>
                    <Dialog.Trigger>
                      <Button variant="destructive" onclick={() => onShelfRednoteDialog()}>Onshelf RedNote
                      </Button>
                    </Dialog.Trigger>
                  </Tooltip.Trigger>
                  <Tooltip.Content>
                    <p>Onshelf product to Rednote</p>
                  </Tooltip.Content>
                </Tooltip.Root>
              </Tooltip.Provider>
            </Dialog.Trigger>
          </div>

          <Dialog.Content>
            <Dialog.Header>
              <Dialog.Title>{dialog_title}</Dialog.Title>
              <Dialog.Description>
                {dialog_body}
              </Dialog.Description>
            </Dialog.Header>
            <Dialog.Footer>
              <Dialog.Footer>
                <Button onclick={() => open = false} type="reset">Cancel</Button>
                <Button class="bg-red-500 hover:bg-red-500" onclick={() => handler()} type="submit">Continue
                </Button>
              </Dialog.Footer>
            </Dialog.Footer>
          </Dialog.Content>
        </Dialog.Root>
        <div class="items-center justify-between px-4 text-4xl">Shadow Product Update History</div>
        <div class="items-center justify-between px-4">
          <HistoryDataTable {histories}/>
        </div>
      </div>
    {:else}
      <div class="items-center justify-between px-4 text-4xl">Please select a valid product from <a
        class="italic font-medium text-blue-600 dark:text-blue-500 hover:underline" href='/product'>All Products</a>
        or <a class="italic font-medium text-blue-600 dark:text-blue-500 hover:underline" href='/shadow'>Shadow
          Products</a> page, and navigate here by clicking "Product OnShelf" menu item.
      </div>
    {/if}
  </main>
</Sidebar.Inset>