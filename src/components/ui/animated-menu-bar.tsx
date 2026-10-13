import React from 'react';

export interface MenuItemConfig<T extends string = string> {
  key: T;
  label: string;
  icon: React.ReactNode;
}

export interface MenuBarProps<T extends string = 'dashboard' | 'notifications' | 'settings' | 'help' | 'security'> {
  active?: T;
  onSelect?: (key: T) => void;
  items?: MenuItemConfig<T>[];
  className?: string;
  size?: 'default' | 'sm';
}

export const defaultIcons = {
  dashboard: (
    <svg width="19" height="19" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
      <path d="M3 9.5L12 4l9 5.5v7.5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9.5z" />
      <path d="M9 22V12h6v10" />
    </svg>
  ),
  notifications: (
    <svg width="19" height="19" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
      <path d="M18 16v-5a6 6 0 1 0-12 0v5l-2 2v1h16v-1l-2-2z" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  ),
  settings: (
    <svg width="19" height="19" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h.09a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51h.09a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v.09a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </svg>
  ),
  help: (
    <svg width="19" height="19" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10" />
      <path d="M9.09 9a3 3 0 1 1 5.82 1c0 2-3 3-3 3" />
      <circle cx="12" cy="17" r="1" />
    </svg>
  ),
  security: (
    <svg width="19" height="19" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  ),
};

interface IconButtonProps {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  onClick?: () => void;
  size?: 'default' | 'sm';
}

const IconButton: React.FC<IconButtonProps> = ({ icon, label, active, onClick, size = 'default' }) => {
  const [hovered, setHovered] = React.useState(false);
  const [showTooltip, setShowTooltip] = React.useState(false);
  const tooltipTimeout = React.useRef<ReturnType<typeof setTimeout> | null>(null);

  const isSmall = size === 'sm';
  const baseBtnSize = isSmall ? 36 : 42;
  const charWidth = isSmall ? 7.2 : 8.5;
  const padding = isSmall ? 18 : 28;

  // Calculate width based on label length
  const expandedWidth = Math.max(baseBtnSize + label.length * charWidth + padding, isSmall ? 92 : 115);

  // Responsive: expand on hover or when active
  const isExpanded = hovered || active;

  // Show tooltip on mobile tap
  const handleMobileTooltip = (e: React.MouseEvent) => {
    if (typeof window !== 'undefined' && window.innerWidth < 640) {
      e.preventDefault();
      setShowTooltip(true);
      if (tooltipTimeout.current) clearTimeout(tooltipTimeout.current);
      tooltipTimeout.current = setTimeout(() => setShowTooltip(false), 1200);
    }
    if (onClick) onClick();
  };

  React.useEffect(() => () => {
    if (tooltipTimeout.current) clearTimeout(tooltipTimeout.current);
  }, []);

  return (
    <button
      type="button"
      aria-label={label}
      className={`group flex items-center rounded-full transition-all duration-300 ease-out focus:outline-none relative overflow-visible cursor-pointer select-none
        ${isSmall ? 'w-9 sm:w-auto px-0 sm:px-2.5 text-xs' : 'w-10.5 sm:w-auto px-0 sm:px-3.5 text-sm'}
        justify-center sm:justify-start
      `}
      style={{
        minWidth: baseBtnSize,
        minHeight: baseBtnSize,
        paddingTop: isSmall ? 5 : 7,
        paddingBottom: isSmall ? 5 : 7,
        background: active
          ? 'linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(245, 248, 252, 0.92) 100%)'
          : hovered
          ? 'linear-gradient(180deg, rgba(255, 255, 255, 0.65) 0%, rgba(255, 255, 255, 0.35) 100%)'
          : 'transparent',
        border: active
          ? '1px solid rgba(255, 255, 255, 1)'
          : hovered
          ? '1px solid rgba(255, 255, 255, 0.75)'
          : '1px solid transparent',
        boxShadow: active
          ? '0 4px 14px -1px rgba(15, 23, 42, 0.12), 0 2px 5px -1px rgba(15, 23, 42, 0.06), inset 0 1px 1px 0 #ffffff, inset 0 -1px 1px 0 rgba(0, 0, 0, 0.04)'
          : hovered
          ? '0 3px 10px rgba(0, 0, 0, 0.04), inset 0 1px 1px rgba(255, 255, 255, 0.85)'
          : 'none',
        color: active ? '#0f172a' : hovered ? '#0f172a' : '#475569',
        fontWeight: active ? 600 : 500,
        transform: hovered && !active ? 'translateY(-1px)' : 'none',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={handleMobileTooltip}
    >
      {/* iOS-style Tooltip for mobile view */}
      <span
        className={`sm:hidden absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-900/90 backdrop-blur-md text-white text-[11px] font-medium rounded-full px-2.5 py-0.5 shadow-md transition-all duration-200 pointer-events-none z-30
          ${showTooltip ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}
      >
        {label}
      </span>

      {/* Icon with smooth micro-scale on hover */}
      <span
        className={`flex items-center justify-center shrink-0 transition-transform duration-300 ease-out group-hover:scale-110 ${
          isSmall ? 'w-4.5 h-4.5' : 'w-5.5 h-5.5'
        }`}
      >
        {icon}
      </span>

      {/* Label expanding smoothly */}
      <span
        className={`${isSmall ? 'text-xs' : 'text-sm'} tracking-tight transition-all duration-300 ease-out whitespace-nowrap pointer-events-none ml-1.5
          hidden sm:inline
          ${isExpanded ? 'opacity-100 w-auto' : 'opacity-0 w-0'}`}
        style={{
          width: isExpanded ? expandedWidth - baseBtnSize - padding : 0,
        }}
      >
        {label}
      </span>
    </button>
  );
};

export function MenuBar<T extends string = 'dashboard' | 'notifications' | 'settings' | 'help' | 'security'>({
  active = 'dashboard' as T,
  onSelect,
  items,
  className = '',
  size = 'default',
}: MenuBarProps<T>) {
  const isSmall = size === 'sm';

  const glassStyle: React.CSSProperties = {
    background:
      'linear-gradient(135deg, rgba(255, 255, 255, 0.72) 0%, rgba(245, 248, 252, 0.45) 50%, rgba(255, 255, 255, 0.62) 100%)',
    backdropFilter: 'blur(24px) saturate(190%)',
    WebkitBackdropFilter: 'blur(24px) saturate(190%)',
    border: '1px solid rgba(255, 255, 255, 0.85)',
    borderTop: '1px solid rgba(255, 255, 255, 0.98)',
    boxShadow:
      '0 12px 36px -4px rgba(15, 23, 42, 0.08), 0 4px 12px -2px rgba(15, 23, 42, 0.04), inset 0 1px 2px 0 rgba(255, 255, 255, 0.95), inset 0 -1px 2px 0 rgba(0, 0, 0, 0.03)',
  };

  const dividerStyle: React.CSSProperties = {
    background:
      'linear-gradient(180deg, rgba(203, 213, 225, 0.1) 0%, rgba(148, 163, 184, 0.6) 50%, rgba(203, 213, 225, 0.1) 100%)',
    boxShadow: '1px 0 0 0 rgba(255, 255, 255, 0.9)',
  };

  if (items && items.length > 0) {
    return (
      <nav
        style={glassStyle}
        className={`relative flex items-center rounded-full ${
          isSmall ? 'gap-1 p-1' : 'gap-1.5 p-1.5'
        } w-fit mx-auto transition-all duration-300 ease-out select-none ${className}`}
      >
        {items.map((item, idx) => (
          <React.Fragment key={item.key}>
            {idx === 2 && (
              <div
                style={dividerStyle}
                className="w-px h-5 mx-1 shrink-0"
              />
            )}
            <IconButton
              icon={item.icon}
              label={item.label}
              active={active === item.key}
              onClick={() => onSelect?.(item.key)}
              size={size}
            />
          </React.Fragment>
        ))}
      </nav>
    );
  }

  return (
    <nav
      style={glassStyle}
      className={`relative flex items-center rounded-full ${
        isSmall ? 'gap-1 p-1' : 'gap-1.5 p-1.5'
      } w-fit mx-auto transition-all duration-300 ease-out select-none ${className}`}
    >
      <IconButton
        icon={defaultIcons.dashboard}
        label="Dashboard"
        active={active === ('dashboard' as T)}
        onClick={() => onSelect?.('dashboard' as T)}
        size={size}
      />
      <div style={dividerStyle} className="w-px h-5 mx-1 shrink-0" />
      <IconButton
        icon={defaultIcons.notifications}
        label="Notifications"
        active={active === ('notifications' as T)}
        onClick={() => onSelect?.('notifications' as T)}
        size={size}
      />
      <IconButton
        icon={defaultIcons.settings}
        label="Settings"
        active={active === ('settings' as T)}
        onClick={() => onSelect?.('settings' as T)}
        size={size}
      />
      <IconButton
        icon={defaultIcons.help}
        label="Help"
        active={active === ('help' as T)}
        onClick={() => onSelect?.('help' as T)}
        size={size}
      />
      <IconButton
        icon={defaultIcons.security}
        label="Security"
        active={active === ('security' as T)}
        onClick={() => onSelect?.('security' as T)}
        size={size}
      />
    </nav>
  );
}

export default MenuBar;
