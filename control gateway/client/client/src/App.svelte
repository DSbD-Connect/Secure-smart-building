<script lang="ts">

  import { onMount } from 'svelte'
  type EventCallback<T> = (event: T) => void;

  import { Button } from "$lib/components/ui/button/index.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import { Label } from "$lib/components/ui/label/index.js";
  import * as Card from "$lib/components/ui/card";
  import { AspectRatio } from "$lib/components/ui/aspect-ratio";
  import { toast } from "svelte-sonner";
  import { Toaster } from "$lib/components/ui/sonner";
  import { Switch } from "$lib/components/ui/switch";

  import { persistentWritable } from '$lib/store'
  
  
  import { House } from 'lucide-svelte';
  import { Thermometer } from 'lucide-svelte';
  import { Droplets } from 'lucide-svelte';
  import { TriangleAlert } from 'lucide-svelte';
  import { Signal } from 'lucide-svelte';
  import { SquareArrowUp } from 'lucide-svelte';
  import { ArrowBigUpDash } from 'lucide-svelte';
  import { BatteryCharging } from 'lucide-svelte';
  import { BatteryMedium } from 'lucide-svelte';
  import { PlugZap } from 'lucide-svelte';
  import { Video } from 'lucide-svelte';
  import { Clock4 } from 'lucide-svelte';
  import { TextCursorInput } from 'lucide-svelte';
  import { Cog } from 'lucide-svelte';
  import { CircleEllipsis } from 'lucide-svelte';
  import { ToggleLeft } from 'lucide-svelte';
  import { Lightbulb } from 'lucide-svelte';
  import { SquareArrowRight } from 'lucide-svelte';
  import { User } from 'lucide-svelte';
  //import { onDestroy } from 'svelte'
  
  let user_value: any
  //user.subscribe((u) => (user_value = u))
  //let unsubscribe = user.subscribe((u) => (user_value = u))

  let username: string;
  let password: string;
  let access_token: string
  let loginSuccessful = false;
  let cheri_on = false;
  let fetched_data: any[] = [];
  let camera_data : {[key:string]:string} = {};

  const user = persistentWritable('user', {
    username: '',
    access_token: ''
  });

  let interval: number | undefined;
  onMount(() => {
    fetch_data();
    console.log(interval);
    if (interval===undefined && $user.username)
        interval = setInterval(fetch_data, 3000);

    //const interval_cameras = setInterval(fetch_cameras, 2000);
  });
  
  // Update user data
  function updateUser(username: any, access_token: any) {
    user.set({ username, access_token });
  }

  function clearUser(){
    user.set({
        username: '',
        access_token: ''
    });
  }

  async function handleLogin(){
      if (!username || !password){
          alert("Please enter your credentials");
      }

      const res = await fetch('/api/login', {
        method: 'POST',
        headers: {
              
              'Content-Type': 'application/json'
        },
        body: JSON.stringify({"username":username, "password":password, "cheri_on":cheri_on})       
      });

      const result_json = await res.json()
      if (res.status == 200){
          loginSuccessful = true;
          
          access_token = result_json["TOKEN"]
          updateUser(username, access_token)
          
          await fetch_data();
          toast_message("User Logged In", username);
          interval = setInterval(fetch_data, 3000);
      }else{
        toast_message("Inccorrect Credentials", username);
      }        
  }

  async function handleLogout(){
    clearUser();
    toast_message("User Logged Out", username);
    clearInterval(interval);
  }

  async function fetch_data(){
      const res = await fetch('/api/devices_entities/'+$user.username, {
          method: 'GET',
          headers: {
              'Authorization': 'Bearer ' + $user.access_token,
              'Content-Type': 'application/json'
          }
      });
     
      fetched_data = await res.json()
      console.log(fetched_data);
      fetch_cameras();

  }

  async function fetch_cameras(){
    for (let flat of fetched_data)
        for (let entity of flat.entities){
            if (entity.entity_id.startsWith("camera.")){
                var image_data = await fetch_camera(entity.entity_id)
                camera_data[entity.entity_id] = image_data
                document.getElementById(entity.entity_id)?.setAttribute("src", camera_data[entity.entity_id]);
            }
                
        }
  }
  async function update_entity_local(updated_entity: { entity_id: any; }){
    for (let flat of fetched_data)
        for (let entity of flat.entities){
            if (entity.entity_id == updated_entity.entity_id){
                entity =updated_entity
            }
        }
        
  }
  async function fetch_camera(entity_id:string){
    
    const res = await fetch('/api/camera/'+entity_id, {
          method: 'GET',
          headers: {
              'Authorization': 'Bearer ' + $user.access_token,
              'Content-Type': 'application/json'
          }
      });

    //return await(res.text())
    return  URL.createObjectURL(await res.blob());
  }
  
  function toast_message(message:string, description:string ){
    toast.success(message, {
      description: description
      
    });
  }
  function get_entity_type(entity: { entity_id: string; attributes: { device_class: string; }; }){
    if (entity.entity_id.startsWith("sensor")){
        if (entity.attributes.device_class == "temperature")            
            return "temperature";
        else if (entity.attributes.device_class == "timestamp")
            return "timestamp";
        else if (entity.attributes.device_class == "humidity")
            return "humidity";
        else if (entity.attributes.device_class == "power")
            return "power";
        else if (entity.attributes.device_class == "energy")
            return "energy";
        else if (entity.attributes.device_class == "voltage")
            return "voltage";
        else if (entity.attributes.device_class == "current")
            return "current";
        else
            return "generic_device";
    } else if (entity.entity_id.startsWith("binary_sensor")){
        if (entity.attributes.device_class == "problem")            
            return "problem";
        else if (entity.attributes.device_class == "connectivity")
            return "connectivity";
        else if (entity.attributes.device_class == "update")
            return "update";
        else
            return "generic_device";
    } else if (entity.entity_id.startsWith("camera")){
        return "camera"
    }  else if (entity.entity_id.startsWith("input_text")){
        return "input_text"
    }  else if (entity.entity_id.startsWith("input_button")){
        return "input_button"
    }else if (entity.entity_id.startsWith("input_boolean")){
        return "toggle"
    }else if (entity.entity_id.startsWith("light")){
        return "light"
    }else if (entity.entity_id.startsWith("switch")){
        return "switch"
    }else if (entity.entity_id.startsWith("person")){
        return "person"
    }else{
        return "generic_entity"
    }


  }
  async function modify_entity(entity: any, event:any){
        
        //var state  = event.detail.currentTarget.dataset.state
        var update_state = "off"
        if (entity.state == "on")
            update_state = "off"
        else
            update_state = "on"

        const res = await fetch('/api/devices_entities/'+entity.entity_id, {
            method: 'POST',
            headers: {
              'Authorization': 'Bearer ' + $user.access_token,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "state":update_state,
                "attributes":entity.attributes
            }
        )
               
        });
        fetch_data()
        //update_entity_local(await res.json())
  }


  async function press_entity(entity: any, event:any){

        const res = await fetch('/api/devices_entities/'+entity.entity_id, {
            method: 'POST',
            headers: {
              'Authorization': 'Bearer ' + $user.access_token,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "state":entity.state,
                "attributes":entity.attributes
            }
        )
               
        });
        fetch_data()
        //update_entity_local(await res.json())
  }

  console.log(loginSuccessful)
  console.log($user.username)
</script>

<main class="grid flex-1 gap-4 p-4 sm:px-20 sm:py-20 md:gap-8" style="justify-content: center;align-items: center">
  
  {#if $user.username != "" }
    <div class= "flex gap-4" style="height:auto">
    {#key fetched_data}
    {#if fetched_data.length > 0}
        {#each fetched_data as flat}
        <div>
            <Card.Root>
                <Card.Header>
                    <Card.Title>
                    <div class="flex items-center justify-between">
                        {flat.area_name}
                        <House />
                    </div>
                </Card.Title>
                    <Card.Description>Devices and Entities</Card.Description>
                </Card.Header>
                <Card.Content>
                    <div class="grid w-full gap-4">
                    {#each flat.entities as entity}
                    <div class="flex items-center justify-between">
                        <div class="pr-5">
                            {#if get_entity_type(entity) == "temperature"}
                                <Thermometer />
                            {:else if get_entity_type(entity) == "humidity"}
                                <Droplets />    
                            {:else if get_entity_type(entity) == "problem"}
                                <TriangleAlert />
                            {:else if get_entity_type(entity) == "connectivity"}
                                <Signal /> 
                            {:else if get_entity_type(entity) == "update"}
                                <ArrowBigUpDash />
                            {:else if get_entity_type(entity) == "power"}
                                <BatteryCharging />
                            {:else if get_entity_type(entity) == "energy"}
                                <BatteryMedium />
                            {:else if get_entity_type(entity) == "voltage"}
                                <BatteryMedium />
                            {:else if get_entity_type(entity) == "current"}
                                <PlugZap />
                            {:else if get_entity_type(entity) == "camera"}
                                <Video />
                            {:else if get_entity_type(entity) == "timestamp"}
                                <Clock4 />
                            {:else if get_entity_type(entity) == "input_text"}
                                <TextCursorInput />
                            {:else if get_entity_type(entity) == "input_button"}
                                <SquareArrowRight />
                            {:else if get_entity_type(entity) == "toggle"}
                                <ToggleLeft />
                            {:else if get_entity_type(entity) == "light"}
                                <Lightbulb />
                            {:else if get_entity_type(entity) == "switch"}
                                <ToggleLeft />
                            {:else if get_entity_type(entity) == "person"}
                                <User />
                            {:else if get_entity_type(entity) == "generic_device"}
                                <Cog />
                            {:else if get_entity_type(entity) == "generic_entity"}
                                <CircleEllipsis />

                            {/if}
                        </div>
                        <div class=" pr-40">
                            <Label class="whitespace-no-wrap">{entity.attributes.friendly_name}</Label>
                        </div>
                        <div class="flex-1 text-right">
                        {#if get_entity_type(entity) == "toggle" || get_entity_type(entity) == "switch" || get_entity_type(entity) == "light" }
                                <Switch checked={entity.state === "on"} on:click={(event) => modify_entity(entity, event)}/>
                            {:else if get_entity_type(entity) == "input_button"}
                                <Button on:click={(event) => press_entity(entity, event)}> Press </Button>
                            {:else}
                                <Label>{entity.state}</Label>
                            {/if}
                        </div>
                        </div>
                    {#if get_entity_type(entity) == "camera"}
                        <div class="flex w-[500px]" style:max-height="500px">
                            <img id="{entity.entity_id}" alt="{entity.entity_id}" src={camera_data[entity.entity_id]} class="rounded-md object-cover" height="500px"/>
                        </div>    
                    {/if}
                    {/each}
                    </div>
                </Card.Content>
            </Card.Root>
        </div>
        {/each}
        {:else}
        No data to show or Home Assistant unresponsive.
        {/if}
        {/key}
    </div>
    <div class="flex ml-auto items-center justify-end space-x-4">
        <Label> Logged in as {$user.username}</Label>
        <Button class="gap-1" variant="destructive" on:click={handleLogout}>Logout</Button>
    </div>
  
  {:else}

      <div class="flex items-center gap-4">
          <Card.Root>
              <Card.Header>
                  <Card.Title>Login</Card.Title>
                  <Card.Description>Use your username and password provided by the building administration.</Card.Description>
              </Card.Header>
              <Card.Content>
                  <form on:submit|preventDefault={handleLogin}>
                      <div class="grid w-full items-center gap-4">
                      <div class="flex flex-col space-y-1.5">
                          <Label for="username">Username</Label>
                          <Input id="username" placeholder="Username" bind:value={username}/>
                          
                      </div>
                      <div class="flex flex-col space-y-1.5">
                          <Label for="password">Password</Label>
                          <Input id="password" placeholder="Password" type="password" bind:value={password} />
                      </div>
                      </div>
                  </form>
              
              </Card.Content>
              <Card.Footer class="flex justify-right">
                <div class="flex ml-auto items-center justify-end space-x-4" >
                  {#if cheri_on}
                    <Label for="cheri_on">CHERI On</Label>
                  {:else}
                    <Label for="cheri_on">CHERI Off</Label>
                  {/if}
                  <Switch id="cheri_on" bind:checked={cheri_on}/>
                  <Button on:click={handleLogin}>Submit</Button>
                </div>
                  
              </Card.Footer>
          </Card.Root>            
      </div>
  {/if}
  
</main>

<Toaster />
