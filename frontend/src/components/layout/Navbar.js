import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Divider,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  AccountCircle,
  Dashboard,
  Security,
  School,
  History,
  Settings,
  ExitToApp,
  Menu as MenuIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Navbar = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [anchorEl, setAnchorEl] = useState(null);
  const [mobileMenuAnchor, setMobileMenuAnchor] = useState(null);

  const handleUserMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };

  const handleMobileMenuOpen = (event) => {
    setMobileMenuAnchor(event.currentTarget);
  };

  const handleMobileMenuClose = () => {
    setMobileMenuAnchor(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    handleUserMenuClose();
  };

  const handleNavigation = (path) => {
    navigate(path);
    handleUserMenuClose();
    handleMobileMenuClose();
  };

  const navigationItems = [
    { label: 'Verify', path: '/verify', icon: <Security /> },
    { label: 'Learn', path: '/learn', icon: <School /> },
    { label: 'History', path: '/history', icon: <History /> },
  ];

  const userMenuItems = [
    { label: 'Dashboard', path: '/dashboard', icon: <Dashboard /> },
    { label: 'Profile', path: '/profile', icon: <AccountCircle /> },
    { label: 'Settings', path: '/settings', icon: <Settings /> },
  ];

  return (
    <AppBar position="static" color="primary" elevation={2}>
      <Toolbar>
        {/* Logo */}
        <Typography
          variant="h6"
          component="div"
          sx={{
            flexGrow: isMobile ? 1 : 0,
            cursor: 'pointer',
            fontWeight: 'bold',
            mr: 4
          }}
          onClick={() => navigate('/')}
        >
          MitraVerify
        </Typography>

        {/* Desktop Navigation */}
        {!isMobile && (
          <Box sx={{ display: 'flex', gap: 1, flexGrow: 1 }}>
            {user && navigationItems.map((item) => (
              <Button
                key={item.path}
                color="inherit"
                startIcon={item.icon}
                onClick={() => handleNavigation(item.path)}
                sx={{ textTransform: 'none' }}
              >
                {item.label}
              </Button>
            ))}
          </Box>
        )}

        {/* Right side buttons */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {user ? (
            <>
              {/* Mobile menu button */}
              {isMobile && (
                <IconButton
                  color="inherit"
                  onClick={handleMobileMenuOpen}
                >
                  <MenuIcon />
                </IconButton>
              )}

              {/* User menu */}
              <IconButton
                onClick={handleUserMenuOpen}
                color="inherit"
              >
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                  {user.username?.charAt(0).toUpperCase()}
                </Avatar>
              </IconButton>

              {/* User dropdown menu */}
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleUserMenuClose}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
              >
                <MenuItem disabled>
                  <Typography variant="subtitle2">
                    Welcome, {user.username}
                  </Typography>
                </MenuItem>
                <Divider />
                {userMenuItems.map((item) => (
                  <MenuItem
                    key={item.path}
                    onClick={() => handleNavigation(item.path)}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {item.icon}
                      {item.label}
                    </Box>
                  </MenuItem>
                ))}
                <Divider />
                <MenuItem onClick={handleLogout}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ExitToApp />
                    Logout
                  </Box>
                </MenuItem>
              </Menu>
            </>
          ) : (
            <>
              <Button color="inherit" onClick={() => navigate('/login')}>
                Login
              </Button>
              <Button
                variant="outlined"
                color="inherit"
                onClick={() => navigate('/register')}
                sx={{ borderColor: 'white', color: 'white' }}
              >
                Register
              </Button>
            </>
          )}
        </Box>

        {/* Mobile navigation menu */}
        {isMobile && user && (
          <Menu
            anchorEl={mobileMenuAnchor}
            open={Boolean(mobileMenuAnchor)}
            onClose={handleMobileMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            {navigationItems.map((item) => (
              <MenuItem
                key={item.path}
                onClick={() => handleNavigation(item.path)}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {item.icon}
                  {item.label}
                </Box>
              </MenuItem>
            ))}
          </Menu>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
