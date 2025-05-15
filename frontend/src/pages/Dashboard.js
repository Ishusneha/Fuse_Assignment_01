import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Heading,
  useColorModeValue,
} from '@chakra-ui/react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalIncome: 0,
    totalExpenses: 0,
    balance: 0,
  });
  const { token } = useAuth();
  const bgColor = useColorModeValue('white', 'gray.700');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/v1/transactions', {
          headers: { Authorization: `Bearer ${token}` },
        });

        const transactions = response.data;
        console.log('Fetched transactions for stats:', transactions);
        
        const income = transactions
          .filter(t => t.type === 'income')
          .reduce((sum, t) => sum + parseFloat(t.amount), 0);
        const expenses = transactions
          .filter(t => t.type === 'expense')
          .reduce((sum, t) => sum + parseFloat(t.amount), 0);

        setStats({
          totalIncome: income,
          totalExpenses: expenses,
          balance: income - expenses,
        });
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };

    if (token) {
      fetchStats();
    }
  }, [token]);

  return (
    <Box>
      <Heading mb={6}>Financial Overview</Heading>
      <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={6}>
        <Stat p={6} bg={bgColor} borderRadius="lg" shadow="sm">
          <StatLabel fontSize="lg">Total Income</StatLabel>
          <StatNumber color="green.500">
            ${stats.totalIncome.toFixed(2)}
          </StatNumber>
          <StatHelpText>All time earnings</StatHelpText>
        </Stat>

        <Stat p={6} bg={bgColor} borderRadius="lg" shadow="sm">
          <StatLabel fontSize="lg">Total Expenses</StatLabel>
          <StatNumber color="red.500">
            ${stats.totalExpenses.toFixed(2)}
          </StatNumber>
          <StatHelpText>All time spending</StatHelpText>
        </Stat>

        <Stat p={6} bg={bgColor} borderRadius="lg" shadow="sm">
          <StatLabel fontSize="lg">Current Balance</StatLabel>
          <StatNumber color={stats.balance >= 0 ? 'blue.500' : 'red.500'}>
            ${stats.balance.toFixed(2)}
          </StatNumber>
          <StatHelpText>Available funds</StatHelpText>
        </Stat>
      </Grid>
    </Box>
  );
};

export default Dashboard; 