
---

# Project Name

This Django project is a file storage application that allows users to upload, manage, and share files securely. It integrates with AWS S3 for scalable and reliable file storage.

## Features

- **User Authentication**: Register, login, and activate accounts with email confirmation.
- **File Upload and Management**: Upload files, categorize them by type, manage access permissions, and delete files.
- **Access Control**: Grant or revoke access to files for specific users.
- **File Download**: Users can download files they have access to using pre-signed URLs from AWS S3.
- **Search and Pagination**: Search files by name and paginate results for better user experience.
- **Responsive Design**: The application is designed to be responsive for various screen sizes.

## Technologies Used

- **Django**: Python web framework for backend development.
- **AWS S3**: Cloud storage service for storing uploaded files securely.
- **Bootstrap**: Frontend framework for responsive design and UI components.
- **Python 3.x**: Programming language used for backend logic.
- **HTML/CSS**: Frontend markup and styling.

## Setup

1. **Clone the Repository**: `git clone <repository_url>`
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Database Migration**: `python manage.py migrate`
4. **Set Up AWS S3**: Configure AWS credentials in `settings.py` for file storage.
5. **Run the Development Server**: `python manage.py runserver`

Access the application at [http://localhost:8000](http://localhost:8000).



## License

[MIT License](LICENSE)

