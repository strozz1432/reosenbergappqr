/// Default API URL for desktop / simulator on same machine.
/// On a physical iPhone, set the API base URL on the login screen to
/// `http://<your-pc-lan-ip>:8000`.
const String kDefaultApiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://127.0.0.1:8000',
);
