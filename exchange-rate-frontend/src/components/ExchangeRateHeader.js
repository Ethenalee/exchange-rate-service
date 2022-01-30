import Typography from '@mui/material/Typography';
import CurrencyExchangeIcon from '@mui/icons-material/CurrencyExchange';

const ExchangeRateHeader = () => {
	return (
		<Typography
			variant='h2'
			component='div'
			data-testid='exchange-rate-header'
			style={{ padding: '3%', fontWeight: 'bold', display: 'flex', columnGap: '2%' }}
		>
			<CurrencyExchangeIcon fontSize="60px" /> Exchange Currnecy
		</Typography>
	);
};

export default ExchangeRateHeader;
