import { useState, useEffect } from 'react';
import axios from 'axios';
import fetchCurrencyData from '../api/fetchCurrencyData';
import { RATE_URL } from '../constants/url';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import OutlinedInput from '@mui/material/OutlinedInput';
import TextField from '@mui/material/TextField';

const ExchangeRatePaper = () => {
	const [currencyData, setCurrencyData] = useState();
	const [baseCurrency, setBaseCurrency] = useState('');
	const [quoteCurrency, setQuoteCurrency] = useState('');
	const [amount, setAmount] = useState('');
	const [resultCurrency, setResultCurrency] = useState('');
	const [resultAmount, setResultAmount] = useState('');
	const url =
		RATE_URL +
		'?base_currency=' +
		baseCurrency +
		'&quote_currency=' +
		quoteCurrency +
		'&amount=' +
		amount;

	useEffect(() => {
		initialLoad();
	}, []);

	const initialLoad = async () => {
		const { data } = await fetchCurrencyData();
		setCurrencyData(data);
	};

	const handleBaseCurrencyChange = (event) => {
		setBaseCurrency(event.target.value);
	};

	const handleQuoteCurrencyChange = (event) => {
		setQuoteCurrency(event.target.value);
	};

	const handleAmountChange = (event) => {
		setAmount(event.target.value);
	};

	const handleClick = () => {
		axios.post(url).then((response) => {
			const data = response['data']['data'];
			setResultCurrency(data['quote_currency']);
			setResultAmount(data['amount']);
		});
	};

	return (
			<Paper
				data-testid='exchange-rate-paper'
				style={{
					minHeight: '30vh',
					padding: '3%',
					display: 'flex',
					flexDirection: 'column',
					justifyContent: 'space-around'
				}}
				variant="outlined"
			>
				<div style={{
					display: 'flex',
					flexDirection: 'row',
					justifyContent: 'space-between',
				}}>
				<FormControl style={{ width: '25%' }}>
					<InputLabel htmlFor='outlined-adornment-amount'>Amount</InputLabel>
					<OutlinedInput
						id='outlined-adornment-amount'
						value={amount}
						onChange={handleAmountChange}
						label='Amount'
					/>
				</FormControl>
				<FormControl style={{ width: '25%' }}>
					<InputLabel id='demo-simple-select-label'>Base Currency</InputLabel>
					<Select
						labelId='demo-simple-select-label'
						id='demo-simple-select'
						value={baseCurrency}
						label='Base Currency'
						onChange={handleBaseCurrencyChange}
					>
						{currencyData &&
							currencyData.map((currency) => (
								<MenuItem value={currency} key={currency}>
									{currency}
								</MenuItem>
							))}
					</Select>
				</FormControl>
				<FormControl 	style={{ width: '25%' }}>
					<InputLabel id='demo-simple-select-label'>Quote Currency</InputLabel>
					<Select
						labelId='demo-simple-select-label'
						id='demo-simple-select'
						value={quoteCurrency}
						label='Quote Currency'
						onChange={handleQuoteCurrencyChange}
					>
						{currencyData &&
							currencyData.map(
								(currency) =>
									currency !== baseCurrency && (
										<MenuItem value={currency} key={currency}>
											{currency}
										</MenuItem>
									),
							)}
					</Select>
				</FormControl>
				<Button
					variant='outlined'
					style={{ width: '10%' }}
					onClick={handleClick}
				>
					Request
				</Button>
				</div>
				<TextField
					id='filled-read-only-input'
					label='Converted Amount'
					value={resultAmount + ' ' + resultCurrency}
					InputProps={{
						readOnly: true,
					}}
				/>
			</Paper>
	);
};

export default ExchangeRatePaper;
