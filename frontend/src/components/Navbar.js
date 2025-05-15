import React from 'react';
import { Box, Flex, Button, Heading, HStack } from '@chakra-ui/react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Box bg="white" px={4} shadow="sm">
      <Flex h={16} alignItems="center" justifyContent="space-between" maxW="1200px" mx="auto">
        <Heading as={RouterLink} to="/" size="lg" color="blue.500">
          Finance Tracker
        </Heading>

        <HStack spacing={4}>
          {user ? (
            <>
              <Button as={RouterLink} to="/" variant="ghost">
                Dashboard
              </Button>
              <Button as={RouterLink} to="/transactions" variant="ghost">
                Transactions
              </Button>
              <Button onClick={handleLogout} colorScheme="red" variant="outline">
                Logout
              </Button>
            </>
          ) : (
            <>
              <Button as={RouterLink} to="/login" variant="ghost">
                Login
              </Button>
              <Button as={RouterLink} to="/register" colorScheme="blue">
                Register
              </Button>
            </>
          )}
        </HStack>
      </Flex>
    </Box>
  );
};

export default Navbar; 