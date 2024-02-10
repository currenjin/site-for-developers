<script>
  import "./styles.css";
  import { page } from "$app/stores";
  import { ChevronDownOutline } from "flowbite-svelte-icons";
  import {
    Navbar,
    NavBrand,
    NavLi,
    NavUl,
    NavHamburger,
    Dropdown,
    DropdownItem,
    DropdownDivider,
  } from "flowbite-svelte";
  $: activeUrl = $page.url.pathname;
</script>

<div class="app">
  <Navbar class="py-2.5 fixed w-full z-20 top-0 start-0 border-b">
    <NavBrand href="/">
      <img
        src="/images/flowbite-svelte-icon-logo.svg"
        class="me-3 h-6 sm:h-9"
        alt="Flowbite Logo"
      />
      <span class="self-center whitespace-nowrap text-xl font-semibold"
        >Site For Developers</span
      >
    </NavBrand>
    <NavHamburger />
    <NavUl {activeUrl}>
      <NavLi href="/">Home</NavLi>
      <NavLi href="/about">About</NavLi>
      <NavLi href="/docs/components/navbar">Navbar</NavLi>
	  <NavLi class="cursor-pointer">
		Dropdown<ChevronDownOutline class="w-3 h-3 ms-2 text-primary-800 dark:text-white inline" />
	  </NavLi>
	  <Dropdown class="w-44 z-20">
		<DropdownItem href="/">Dashboard</DropdownItem>
		<DropdownItem href="/docs/components/navbar">Settings</DropdownItem>
		<DropdownItem href="/">Earnings</DropdownItem>
		<DropdownDivider />
		<DropdownItem href="/">Sign out</DropdownItem>
	  </Dropdown>
      <NavLi href="/pricing">Pricing</NavLi>
      <NavLi href="/contact">Contact</NavLi>
    </NavUl>
  </Navbar>
  <main class="mt-20">
    <slot />
  </main>
</div>

<style>
</style>
