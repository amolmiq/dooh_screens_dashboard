# DOOH Screens Interactive Dashboard

A professional, client-facing Streamlit dashboard for visualizing and analyzing Digital Out-of-Home (DOOH) screen locations worldwide.

## Features

### 🗺️ Interactive Map Visualization
- **Pin-based map** showing all DOOH screen locations
- **Hover tooltips** displaying key information:
  - Screen name
  - Venue type
  - Media owner
  - City location
  - Dimensions
  - Image/Video capabilities
  - Spot length

### 🔍 Advanced Filtering
- **Country**: Filter screens by country
- **Region**: Filter by state/region
- **Dimensions**: Screen dimensions (W x H)
- **Allow Image**: Yes/No filter
- **Allow Video**: Yes/No filter
- **Spot Length**: Filter by advertisement duration
- **Venue Type**: Filter by location type (Bus Shelters, etc.)

### 📊 Real-time Analytics
- Total screen count
- Country distribution
- Media owner statistics
- Venue type breakdown
- Screen orientation analysis
- Image/Video capability metrics

### 📋 Data Management
- Detailed data table view
- Export filtered data to CSV
- Responsive design for all devices

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Navigate to the project directory:**
   ```bash
   cd "c:\Users\amol.gupta\Desktop\DOOH Screens Info"
   ```

2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify data file:**
   Ensure `DOOH_Screens_data.csv` is present in the project directory.

## Running the Dashboard

### Local Development

Run the following command in your terminal:

```bash
streamlit run app.py
```

The dashboard will automatically open in your default web browser at `http://localhost:8501`

### Optional: Mapbox Basemap

This app supports Mapbox basemaps when a token is provided. Without a token, the app will still render a default basemap.

Set your token in the current session (PowerShell):

```powershell
$env:MAPBOX_API_KEY = "<your_mapbox_token>"; streamlit run app.py
```

### Alternative Port

If port 8501 is already in use:

```bash
streamlit run app.py --server.port 8502
```

## Deployment Options

### 1. Streamlit Community Cloud (Free)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository and branch
6. Set main file path to `app.py`
7. Click "Deploy"

## Deploying on Streamlit Community Cloud

If you can’t commit the hidden `.streamlit` folder, use this alternative config path:

- This repo includes `streamlit_config/config.toml` (non-hidden).
- In your Streamlit app settings (Advanced settings → Environment variables), set:
   - `STREAMLIT_CONFIG=streamlit_config/config.toml`

This ensures the app defaults to the Light theme everywhere. No other server settings are required on Community Cloud.

Note: The EC2/nginx deployment uses `.streamlit/config.toml` which includes a `server.baseUrlPath` for `/dooh_planner`. Do not use that file on Community Cloud.

### 2. Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t dooh-dashboard .
docker run -p 8501:8501 dooh-dashboard
```

### 3. AWS/Azure/GCP

- **AWS**: Deploy using EC2, ECS, or Elastic Beanstalk
- **Azure**: Use Azure App Service or Azure Container Instances
- **GCP**: Deploy on Google App Engine or Cloud Run

## Configuration

### Custom Styling

Create `.streamlit/config.toml` for custom theme:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
```

### Performance Optimization

For large datasets, consider:
- Implementing data pagination
- Adding caching strategies
- Optimizing map rendering for 1000+ pins

## Project Structure

```
DOOH Screens Info/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── DOOH_Screens_data.csv      # Screen location data
└── .streamlit/
    └── config.toml            # Streamlit configuration (optional)
```

## Data Format

The CSV file should contain the following columns:
- Screen name
- Screen latitude
- Screen longitude
- Venue type
- Media owner
- Site location (city)
- Site region (state)
- Country
- Dimensions (W x H)
- Allow Image
- Allow Video
- Spot length
- And other metadata fields

## Troubleshooting

### Map Not Displaying
- Check if latitude/longitude values are valid
- Ensure pydeck is properly installed
- Verify internet connection (map tiles require online access)

### Filters Not Working
- Verify CSV column names match exactly
- Check for missing or null values in filter columns
- Ensure data types are correct

### Performance Issues
- Reduce the number of visible data points
- Implement data sampling for very large datasets
- Use Streamlit's caching mechanisms

## Browser Compatibility

Tested and compatible with:
- Chrome/Edge (Recommended)
- Firefox
- Safari

## Security Considerations

For production deployment:
- Use HTTPS
- Implement authentication if needed
- Sanitize user inputs
- Keep dependencies updated
- Set appropriate CORS policies

## Support & Maintenance

### Updating Data
Simply replace `DOOH_Screens_data.csv` with the updated file and restart the application.

### Adding New Features
The modular code structure allows easy extension:
- Additional filters can be added in the sidebar section
- New visualizations can be added in the chart column
- Custom metrics can be added in the metrics row

## License

This dashboard is proprietary software for internal use.

## Contact

For questions or support, please contact your development team.

---

**Version:** 1.0.0  
**Last Updated:** November 2025  
**Built with:** Streamlit, Pandas, PyDeck, Plotly
