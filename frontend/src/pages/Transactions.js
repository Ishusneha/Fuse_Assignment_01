import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Heading,
  HStack,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  Select,
  useToast,
} from '@chakra-ui/react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { token } = useAuth();
  const toast = useToast();

  const [newTransaction, setNewTransaction] = useState({
    amount: '',
    type: 'expense',
    description: '',
    category_id: '',
    currency: 'USD',
  });

  const fetchTransactions = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/transactions', {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log('Fetched transactions:', response.data);
      setTransactions(response.data);
    } catch (error) {
      console.error('Error fetching transactions:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/categories/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log('Categories:', response.data);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
      toast({
        title: 'Error fetching categories',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  useEffect(() => {
    if (token) {
      fetchTransactions();
      fetchCategories();
    }
  }, [token]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewTransaction((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const transactionData = {
        ...newTransaction,
        amount: parseFloat(newTransaction.amount),
        category_id: parseInt(newTransaction.category_id, 10)
      };

      await axios.post(
        'http://localhost:8000/api/v1/transactions/',
        transactionData,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      toast({
        title: 'Transaction created',
        status: 'success',
        duration: 3000,
      });
      onClose();
      fetchTransactions();
      setNewTransaction({
        amount: '',
        type: 'expense',
        description: '',
        category_id: '',
        currency: 'USD',
      });
    } catch (error) {
      console.error('Error details:', error.response?.data);
      toast({
        title: 'Error creating transaction',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  return (
    <Box>
      <HStack justify="space-between" mb={6}>
        <Heading>Transactions</Heading>
        <Button colorScheme="blue" onClick={onOpen}>
          Add Transaction
        </Button>
      </HStack>

      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Date</Th>
            <Th>Description</Th>
            <Th>Category</Th>
            <Th>Type</Th>
            <Th isNumeric>Amount</Th>
          </Tr>
        </Thead>
        <Tbody>
          {transactions.map((transaction) => {
            console.log('Transaction data:', {
              id: transaction.id,
              category: transaction.category,
              type: transaction.type,
              amount: transaction.amount
            });
            return (
              <Tr key={transaction.id}>
                <Td>{new Date(transaction.date).toLocaleDateString()}</Td>
                <Td>{transaction.description}</Td>
                <Td>{transaction.category?.name || 'N/A'}</Td>
                <Td>{transaction.type}</Td>
                <Td isNumeric color={transaction.type === 'income' ? 'green.500' : 'red.500'}>
                  {transaction.currency} {transaction.amount}
                </Td>
              </Tr>
            );
          })}
        </Tbody>
      </Table>

      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add Transaction</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <form onSubmit={handleSubmit}>
              <FormControl mb={4}>
                <FormLabel>Amount</FormLabel>
                <Input
                  name="amount"
                  type="number"
                  step="0.01"
                  value={newTransaction.amount}
                  onChange={handleInputChange}
                  required
                />
              </FormControl>

              <FormControl mb={4}>
                <FormLabel>Type</FormLabel>
                <Select
                  name="type"
                  value={newTransaction.type}
                  onChange={handleInputChange}
                >
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                </Select>
              </FormControl>

              <FormControl mb={4}>
                <FormLabel>Description</FormLabel>
                <Input
                  name="description"
                  value={newTransaction.description}
                  onChange={handleInputChange}
                  required
                />
              </FormControl>

              <FormControl mb={4}>
                <FormLabel>Category</FormLabel>
                <Select
                  name="category_id"
                  value={newTransaction.category_id}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select category</option>
                  {categories && categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </Select>
              </FormControl>

              <Button type="submit" colorScheme="blue" width="full">
                Add Transaction
              </Button>
            </form>
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default Transactions; 