import { createTheme } from '@mui/material/styles';

// Custom color palette
const colors = {
  primary: {
    50: '#e3f2fd',
    100: '#bbdefb',
    200: '#90caf9',
    300: '#64b5f6',
    400: '#42a5f5',
    500: '#1976d2', // Main primary color
    600: '#1565c0',
    700: '#0d47a1',
    800: '#0d47a1',
    900: '#0d47a1',
  },
  secondary: {
    50: '#fce4ec',
    100: '#f8bbd9',
    200: '#f48fb1',
    300: '#f06292',
    400: '#ec407a',
    500: '#dc004e', // Main secondary color
    600: '#c2185b',
    700: '#ad1457',
    800: '#880e4f',
    900: '#880e4f',
  },
  success: {
    50: '#e8f5e8',
    100: '#c8e6c9',
    200: '#a5d6a7',
    300: '#81c784',
    400: '#66bb6a',
    500: '#2e7d32', // Main success color
    600: '#388e3c',
    700: '#2e7d32',
    800: '#2e7d32',
    900: '#1b5e20',
  },
  warning: {
    50: '#fff8e1',
    100: '#ffecb3',
    200: '#ffe082',
    300: '#ffd54f',
    400: '#ffca28',
    500: '#ed6c02', // Main warning color
    600: '#f57c00',
    700: '#ef6c00',
    800: '#e65100',
    900: '#e65100',
  },
  error: {
    50: '#fdeaea',
    100: '#f8d7da',
    200: '#f5c6cb',
    300: '#f1b0b7',
    400: '#ed969e',
    500: '#d32f2f', // Main error color
    600: '#c62828',
    700: '#b71c1c',
    800: '#b71c1c',
    900: '#b71c1c',
  },
  info: {
    50: '#e0f2f1',
    100: '#b2dfdb',
    200: '#80cbc4',
    300: '#4db6ac',
    400: '#26a69a',
    500: '#0288d1', // Main info color
    600: '#0277bd',
    700: '#01579b',
    800: '#01579b',
    900: '#01579b',
  },
  grey: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#eeeeee',
    300: '#e0e0e0',
    400: '#bdbdbd',
    500: '#9e9e9e',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
  },
};

// Create the theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: colors.primary[500],
      light: colors.primary[300],
      dark: colors.primary[700],
      contrastText: '#ffffff',
    },
    secondary: {
      main: colors.secondary[500],
      light: colors.secondary[300],
      dark: colors.secondary[700],
      contrastText: '#ffffff',
    },
    success: {
      main: colors.success[500],
      light: colors.success[300],
      dark: colors.success[700],
      contrastText: '#ffffff',
    },
    warning: {
      main: colors.warning[500],
      light: colors.warning[300],
      dark: colors.warning[700],
      contrastText: '#ffffff',
    },
    error: {
      main: colors.error[500],
      light: colors.error[300],
      dark: colors.error[700],
      contrastText: '#ffffff',
    },
    info: {
      main: colors.info[500],
      light: colors.info[300],
      dark: colors.info[700],
      contrastText: '#ffffff',
    },
    grey: colors.grey,
    background: {
      default: '#fafafa',
      paper: '#ffffff',
    },
    text: {
      primary: colors.grey[900],
      secondary: colors.grey[600],
      disabled: colors.grey[400],
    },
    divider: colors.grey[200],
  },
  typography: {
    fontFamily: '"Inter", "Poppins", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
    h1: {
      fontFamily: '"Poppins", "Inter", sans-serif',
      fontWeight: 700,
      fontSize: '2.5rem',
      lineHeight: 1.2,
      letterSpacing: '-0.01562em',
      color: colors.grey[900],
    },
    h2: {
      fontFamily: '"Poppins", "Inter", sans-serif',
      fontWeight: 600,
      fontSize: '2rem',
      lineHeight: 1.3,
      letterSpacing: '-0.00833em',
      color: colors.grey[900],
    },
    h3: {
      fontFamily: '"Poppins", "Inter", sans-serif',
      fontWeight: 600,
      fontSize: '1.75rem',
      lineHeight: 1.3,
      letterSpacing: '0em',
      color: colors.grey[900],
    },
    h4: {
      fontFamily: '"Poppins", "Inter", sans-serif',
      fontWeight: 600,
      fontSize: '1.5rem',
      lineHeight: 1.4,
      letterSpacing: '0.00735em',
      color: colors.grey[900],
    },
    h5: {
      fontFamily: '"Poppins", "Inter", sans-serif',
      fontWeight: 600,
      fontSize: '1.25rem',
      lineHeight: 1.4,
      letterSpacing: '0em',
      color: colors.grey[900],
    },
    h6: {
      fontFamily: '"Poppins", "Inter", sans-serif',
      fontWeight: 500,
      fontSize: '1rem',
      lineHeight: 1.5,
      letterSpacing: '0.0075em',
      color: colors.grey[900],
    },
    subtitle1: {
      fontWeight: 500,
      fontSize: '1rem',
      lineHeight: 1.75,
      letterSpacing: '0.00938em',
      color: colors.grey[700],
    },
    subtitle2: {
      fontWeight: 500,
      fontSize: '0.875rem',
      lineHeight: 1.57,
      letterSpacing: '0.00714em',
      color: colors.grey[700],
    },
    body1: {
      fontWeight: 400,
      fontSize: '1rem',
      lineHeight: 1.6,
      letterSpacing: '0.00938em',
      color: colors.grey[800],
    },
    body2: {
      fontWeight: 400,
      fontSize: '0.875rem',
      lineHeight: 1.6,
      letterSpacing: '0.01071em',
      color: colors.grey[700],
    },
    button: {
      fontWeight: 500,
      fontSize: '0.875rem',
      lineHeight: 1.75,
      letterSpacing: '0.02857em',
      textTransform: 'none',
    },
    caption: {
      fontWeight: 400,
      fontSize: '0.75rem',
      lineHeight: 1.66,
      letterSpacing: '0.03333em',
      color: colors.grey[600],
    },
    overline: {
      fontWeight: 500,
      fontSize: '0.75rem',
      lineHeight: 2.66,
      letterSpacing: '0.08333em',
      textTransform: 'uppercase',
      color: colors.grey[600],
    },
  },
  shape: {
    borderRadius: 12,
  },
  spacing: 8,
  shadows: [
    'none',
    '0px 2px 4px rgba(0,0,0,0.1)',
    '0px 4px 8px rgba(0,0,0,0.12)',
    '0px 6px 16px rgba(0,0,0,0.15)',
    '0px 8px 24px rgba(0,0,0,0.18)',
    '0px 12px 32px rgba(0,0,0,0.2)',
    '0px 16px 48px rgba(0,0,0,0.22)',
    '0px 24px 64px rgba(0,0,0,0.25)',
    '0px 32px 80px rgba(0,0,0,0.28)',
    '0px 40px 96px rgba(0,0,0,0.3)',
    '0px 48px 112px rgba(0,0,0,0.32)',
    '0px 56px 128px rgba(0,0,0,0.35)',
    '0px 64px 144px rgba(0,0,0,0.38)',
    '0px 72px 160px rgba(0,0,0,0.4)',
    '0px 80px 176px rgba(0,0,0,0.42)',
    '0px 88px 192px rgba(0,0,0,0.45)',
    '0px 96px 208px rgba(0,0,0,0.48)',
    '0px 104px 224px rgba(0,0,0,0.5)',
    '0px 112px 240px rgba(0,0,0,0.52)',
    '0px 120px 256px rgba(0,0,0,0.55)',
    '0px 128px 272px rgba(0,0,0,0.58)',
    '0px 136px 288px rgba(0,0,0,0.6)',
    '0px 144px 304px rgba(0,0,0,0.62)',
    '0px 152px 320px rgba(0,0,0,0.65)',
    '0px 160px 336px rgba(0,0,0,0.68)',
  ],
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
          WebkitFontSmoothing: 'antialiased',
          MozOsxFontSmoothing: 'grayscale',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
          fontSize: '0.875rem',
          padding: '10px 20px',
          minHeight: 44, // Accessibility
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-1px)',
            boxShadow: '0 4px 8px rgba(0, 0, 0, 0.12)',
          },
        },
        contained: {
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
          '&:hover': {
            boxShadow: '0 4px 8px rgba(0, 0, 0, 0.15)',
          },
        },
        outlined: {
          borderWidth: 2,
          '&:hover': {
            borderWidth: 2,
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
          border: '1px solid #f0f0f0',
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.15)',
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: 24,
          '&:last-child': {
            paddingBottom: 24,
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            '& fieldset': {
              borderWidth: 2,
              borderColor: colors.grey[300],
            },
            '&:hover fieldset': {
              borderColor: colors.grey[400],
            },
            '&.Mui-focused fieldset': {
              borderColor: colors.primary[500],
            },
          },
        },
      },
    },
    MuiInputBase: {
      styleOverrides: {
        root: {
          fontSize: '0.875rem',
        },
        input: {
          padding: '12px 14px',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          fontWeight: 500,
          fontSize: '0.75rem',
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          '& .MuiAlert-icon': {
            fontSize: '1.25rem',
          },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 16,
          padding: 8,
        },
      },
    },
    MuiDialogTitle: {
      styleOverrides: {
        root: {
          fontSize: '1.25rem',
          fontWeight: 600,
          color: colors.grey[900],
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#ffffff',
          color: colors.grey[900],
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          borderBottom: `1px solid ${colors.grey[200]}`,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: `1px solid ${colors.grey[200]}`,
          boxShadow: 'none',
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '4px 8px',
          '&:hover': {
            backgroundColor: colors.grey[50],
          },
          '&.Mui-selected': {
            backgroundColor: colors.primary[50],
            color: colors.primary[700],
            '&:hover': {
              backgroundColor: colors.primary[100],
            },
          },
        },
      },
    },
    MuiListItemIcon: {
      styleOverrides: {
        root: {
          minWidth: 40,
          color: 'inherit',
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: {
          borderBottom: `1px solid ${colors.grey[200]}`,
        },
        indicator: {
          height: 3,
          borderRadius: '3px 3px 0 0',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          fontSize: '0.875rem',
          minHeight: 48,
          '&.Mui-selected': {
            color: colors.primary[600],
          },
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          height: 8,
        },
        bar: {
          borderRadius: 4,
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: colors.grey[800],
          color: '#ffffff',
          fontSize: '0.75rem',
          borderRadius: 6,
          padding: '8px 12px',
        },
        arrow: {
          color: colors.grey[800],
        },
      },
    },
    MuiSnackbar: {
      styleOverrides: {
        root: {
          '& .MuiSnackbarContent-root': {
            borderRadius: 8,
          },
        },
      },
    },
    MuiMenu: {
      styleOverrides: {
        paper: {
          borderRadius: 8,
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.15)',
          border: `1px solid ${colors.grey[200]}`,
        },
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          margin: '2px 8px',
          '&:hover': {
            backgroundColor: colors.grey[50],
          },
        },
      },
    },
  },
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 900,
      lg: 1200,
      xl: 1536,
    },
  },
  zIndex: {
    appBar: 1100,
    drawer: 1200,
    modal: 1300,
    snackbar: 1400,
    tooltip: 1500,
  },
});

// Custom theme extensions
theme.custom = {
  // Custom gradients
  gradients: {
    primary: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)',
    secondary: 'linear-gradient(135deg, #dc004e 0%, #f06292 100%)',
    success: 'linear-gradient(135deg, #2e7d32 0%, #66bb6a 100%)',
    warning: 'linear-gradient(135deg, #ed6c02 0%, #ffb74d 100%)',
    error: 'linear-gradient(135deg, #d32f2f 0%, #ef5350 100%)',
    info: 'linear-gradient(135deg, #0288d1 0%, #4fc3f7 100%)',
  },
  
  // Status colors
  status: {
    verified: {
      color: colors.success[500],
      background: colors.success[50],
      border: colors.success[200],
    },
    questionable: {
      color: colors.warning[600],
      background: colors.warning[50],
      border: colors.warning[200],
    },
    false: {
      color: colors.error[500],
      background: colors.error[50],
      border: colors.error[200],
    },
    insufficient: {
      color: colors.grey[600],
      background: colors.grey[50],
      border: colors.grey[200],
    },
  },
  
  // Layout dimensions
  layout: {
    headerHeight: 64,
    sidebarWidth: 280,
    sidebarCollapsedWidth: 80,
    bottomNavHeight: 56,
    fabSize: 56,
  },
  
  // Animation durations
  transitions: {
    fast: 200,
    normal: 300,
    slow: 500,
  },
};

export default theme;
