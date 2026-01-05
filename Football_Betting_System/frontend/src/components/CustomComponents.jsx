import React from 'react';
import '../styles/CustomComponents.css';

const spacingToPx = (value) => {
  if (value === undefined || value === null || value === '') return undefined;
  if (typeof value === 'number' && Number.isFinite(value)) return `${value * 4}px`;

  const token = String(value);
  const map = {
    xs: 8,
    sm: 12,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
    xxxl: 64,
  };
  if (map[token] !== undefined) return `${map[token]}px`;

  const asNumber = Number(token);
  if (Number.isFinite(asNumber)) return `${asNumber}px`;
  return undefined;
};

// Custom Box Component (basic div wrapper)
export const Box = ({ children, className = '', style = {}, onClick }) => {
  return (
    <div className={`box ${className}`} style={style} onClick={onClick}>
      {children}
    </div>
  );
};

// Custom Card Component
export const Card = ({ 
  children, 
  className = '', 
  padding = 'lg',
  shadow = 'sm',
  radius = 'md',
  withBorder = false,
  style = {},
  onClick,
}) => {
  const classes = [
    'card',
    `card-padding-${padding}`,
    `card-shadow-${shadow}`,
    `card-radius-${radius}`,
    withBorder ? 'card-border' : '',
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} style={style} onClick={onClick}>
      {children}
    </div>
  );
};

// Custom Title Component
export const Title = ({ children, order = 1, className = '', mb, mt, style = {} }) => {
  const Tag = `h${order}`;
  const classes = ['title', `title-${order}`, className].filter(Boolean).join(' ');
  const styles = {
    ...style,
    marginBottom: spacingToPx(mb),
    marginTop: spacingToPx(mt),
  };
  
  return <Tag className={classes} style={styles}>{children}</Tag>;
};

// Custom Text Component
export const Text = ({ 
  children, 
  className = '', 
  size = 'md',
  weight,
  fw,
  color,
  c,
  align,
  mb,
  mt,
  style = {} 
}) => {
  const classes = [
    'text',
    `text-size-${size}`,
    (fw ?? weight) ? `text-weight-${fw ?? weight}` : '',
    (c ?? color) ? `text-color-${c ?? color}` : '',
    align ? `text-align-${align}` : '',
    className,
  ].filter(Boolean).join(' ');

  const styles = {
    ...style,
    marginBottom: spacingToPx(mb),
    marginTop: spacingToPx(mt),
  };

  return <p className={classes} style={styles}>{children}</p>;
};

// Custom Badge Component
export const Badge = ({ 
  children, 
  className = '', 
  color = 'blue',
  variant = 'filled',
  size = 'md',
  style = {} 
}) => {
  const classes = [
    'badge',
    `badge-${color}`,
    `badge-${variant}`,
    `badge-size-${size}`,
    className,
  ].filter(Boolean).join(' ');

  return <span className={classes} style={style}>{children}</span>;
};

// Custom Group Component
export const Group = ({ 
  children, 
  className = '', 
  position = 'left',
  justify,
  spacing = 'md',
  py,
  px,
  mb,
  mt,
  style = {} 
}) => {
  const normalizedPosition = (() => {
    if (justify === 'space-between') return 'apart';
    if (justify === 'center') return 'center';
    if (justify === 'flex-end' || justify === 'right') return 'right';
    if (justify === 'flex-start' || justify === 'left') return 'left';
    return position;
  })();

  const classes = [
    'group',
    `group-${normalizedPosition}`,
    `group-spacing-${spacing}`,
    className,
  ].filter(Boolean).join(' ');

  const styles = {
    ...style,
    gap: spacingToPx(spacing), // Force inline gap
    paddingTop: spacingToPx(py),
    paddingBottom: spacingToPx(py),
    paddingLeft: spacingToPx(px),
    paddingRight: spacingToPx(px),
    marginBottom: spacingToPx(mb),
    marginTop: spacingToPx(mt),
  };

  return <div className={classes} style={styles}>{children}</div>;
};

// Custom Stack Component
export const Stack = ({ 
  children, 
  className = '', 
  spacing = 'md',
  gap,
  align = 'stretch',
  mb,
  mt,
  style = {} 
}) => {
  const spacingToken = gap ?? spacing;
  const classes = [
    'stack',
    typeof spacingToken === 'string' ? `stack-spacing-${spacingToken}` : '',
    `stack-align-${align}`,
    className,
  ].filter(Boolean).join(' ');

  const styles = {
    ...style,
    marginBottom: spacingToPx(mb),
    marginTop: spacingToPx(mt),
    gap: spacingToPx(spacingToken), // Force inline gap
  };

  return <div className={classes} style={styles}>{children}</div>;
};

// Custom Grid Component
export const Grid = ({ children, className = '', gutter = 'md', style = {} }) => {
  const classes = [
    'grid',
    `grid-gutter-${gutter}`,
    className,
  ].filter(Boolean).join(' ');
  
  const styles = {
    ...style,
    gap: spacingToPx(gutter), // Force inline gap
  };
  
  return <div className={classes} style={styles}>{children}</div>;
};

export const GridCol = ({ 
  children, 
  className = '', 
  span = 12,
  md,
  lg,
  style = {} 
}) => {
  // Handle both number and object span formats
  let baseSpan = 12;
  let mdSpan = null;
  let lgSpan = null;

  if (typeof span === 'object' && span !== null) {
    baseSpan = span.base || span.xs || 12;
    mdSpan = span.md;
    lgSpan = span.lg;
  } else {
    baseSpan = span || 12;
    mdSpan = md;
    lgSpan = lg;
  }

  const classes = [
    'grid-col',
    `grid-span-${baseSpan}`,
    mdSpan ? `grid-md-${mdSpan}` : '',
    lgSpan ? `grid-lg-${lgSpan}` : '',
    className,
  ].filter(Boolean).join(' ');

  return <div className={classes} style={style}>{children}</div>;
};

// Also add Grid.Col as a property for JSX dot notation
Grid.Col = GridCol;

// Custom Button Component
export const Button = ({ 
  children, 
  className = '', 
  onClick,
  variant = 'filled',
  color = 'blue',
  size = 'md',
  fullWidth = false,
  loading = false,
  disabled = false,
  leftIcon,
  rightIcon,
  leftSection,
  rightSection,
  style = {} 
}) => {
  const classes = [
    'button',
    `button-${variant}`,
    `button-${color}`,
    `button-size-${size}`,
    fullWidth ? 'button-fullwidth' : '',
    disabled || loading ? 'button-disabled' : '',
    className,
  ].filter(Boolean).join(' ');

  return (
    <button 
      className={classes} 
      onClick={onClick} 
      disabled={disabled || loading}
      style={style}
    >
      {(leftSection || leftIcon) && <span className="button-icon-left">{leftSection || leftIcon}</span>}
      {loading ? 'Loading...' : children}
      {(rightSection || rightIcon) && <span className="button-icon-right">{rightSection || rightIcon}</span>}
    </button>
  );
};

// Custom Loader Component
export const Loader = ({ size = 'md', className = '' }) => {
  const classes = ['loader', `loader-${size}`, className].filter(Boolean).join(' ');
  return <div className={classes}><div className="loader-spinner"></div></div>;
};

// Custom Select Component
export const Select = ({ 
  label,
  placeholder,
  value,
  onChange,
  data = [],
  className = '',
  clearable = false,
  searchable = false,
  disabled = false,
  style = {}
}) => {
  const normalized = (Array.isArray(data) ? data : []).map((item) => {
    if (typeof item === 'string' || typeof item === 'number') {
      const v = String(item);
      return { value: v, label: v };
    }

    if (item && typeof item === 'object') {
      const vRaw = item.value ?? item.label ?? '';
      const lRaw = item.label ?? item.value ?? '';
      const v = String(vRaw);
      const l = String(lRaw);
      if (!v && !l) return null;
      return { value: v || l, label: l || v };
    }

    return null;
  }).filter(Boolean);

  return (
    <div className={`select-wrapper ${className}`} style={style}>
      {label && <label className="select-label">{label}</label>}
      <select 
        className="select" 
        value={value || ''} 
        onChange={(e) => onChange?.(e.target.value)}
        disabled={disabled}
      >
        <option value="">{placeholder || 'Select...'}</option>
        {normalized.map((item) => (
          <option key={item.value} value={item.value}>
            {item.label}
          </option>
        ))}
      </select>
    </div>
  );
};

// Custom NumberInput Component
export const NumberInput = ({ 
  label,
  placeholder,
  value,
  onChange,
  min,
  max,
  step = 1,
  className = '',
  style = {}
}) => {
  return (
    <div className={`input-wrapper ${className}`} style={style}>
      {label && <label className="input-label">{label}</label>}
      <input 
        type="number"
        className="input" 
        value={value || ''} 
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        placeholder={placeholder}
        min={min}
        max={max}
        step={step}
      />
    </div>
  );
};

// Custom Progress Component
export const Progress = ({ 
  value = 0,
  color = 'blue',
  size = 'md',
  className = '',
  label,
  style = {}
}) => {
  const classes = [
    'progress',
    `progress-${color}`,
    `progress-size-${size}`,
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} style={style}>
      <div className="progress-bar" style={{ width: `${value}%` }}>
        {label && <span className="progress-label">{label}</span>}
      </div>
    </div>
  );
};

// Custom Alert Component
export const Alert = ({ 
  children,
  icon,
  title,
  color = 'blue',
  variant = 'filled',
  className = '',
  style = {}
}) => {
  const classes = [
    'alert',
    `alert-${color}`,
    `alert-${variant}`,
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} style={style}>
      {icon && <div className="alert-icon">{icon}</div>}
      <div className="alert-content">
        {title && <div className="alert-title">{title}</div>}
        <div className="alert-body">{children}</div>
      </div>
    </div>
  );
};

// Custom Table Component
export const Table = ({ children, className = '', style = {} }) => {
  return <table className={`table ${className}`} style={style}>{children}</table>;
};

// Table subcomponents for Mantine-like API
const TableThead = ({ children, className = '', style = {} }) => (
  <thead className={className} style={style}>{children}</thead>
);
const TableTbody = ({ children, className = '', style = {} }) => (
  <tbody className={className} style={style}>{children}</tbody>
);
const TableTr = ({ children, className = '', style = {}, onClick }) => (
  <tr className={className} style={style} onClick={onClick}>{children}</tr>
);
const TableTh = ({ children, className = '', style = {} }) => (
  <th className={className} style={style}>{children}</th>
);
const TableTd = ({ children, className = '', style = {} }) => (
  <td className={className} style={style}>{children}</td>
);

Table.Thead = TableThead;
Table.Tbody = TableTbody;
Table.Tr = TableTr;
Table.Th = TableTh;
Table.Td = TableTd;

// Custom Modal Component
export const Modal = ({ 
  opened,
  onClose,
  title,
  children,
  size = 'md',
  className = '',
  style = {}
}) => {
  if (!opened) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className={`modal modal-${size} ${className}`} 
        style={style}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3 className="modal-title">{title}</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>
  );
};
