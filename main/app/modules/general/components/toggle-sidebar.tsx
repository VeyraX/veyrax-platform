import type { ComponentProps } from 'react';
import { type SidebarTrigger, useSidebar } from '@/components/ui/sidebar';
import { PanelRightIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function SidebarToggle({
  className,
}: ComponentProps<typeof SidebarTrigger>) {
  const { toggleSidebar, open } = useSidebar();

  const handleToggle = () => {
    toggleSidebar();
    localStorage.setItem('sidebarState', open ? 'closed' : 'open');
  };

  return (
    <Button
      onClick={handleToggle}
      variant="outline"
      className="md:px-2 md:h-fit"
    >
      <PanelRightIcon size={16} />
    </Button>
  );
}