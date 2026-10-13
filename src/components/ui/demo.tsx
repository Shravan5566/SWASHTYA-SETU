import { MenuBar } from "@/components/ui/animated-menu-bar";
import React, { useState } from 'react'

const menuItems = [
  'dashboard',
  'notifications',
  'settings',
  'help',
  'security',
] as const;
type MenuItem = typeof menuItems[number];

export default function DemoOne() {
  const [active, setActive] = useState<MenuItem>('dashboard');
  return <MenuBar active={active} onSelect={setActive} />;
}
