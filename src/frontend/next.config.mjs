/** @type {import('next').NextConfig} */
const nextConfig = {
    webpack: (config) => {
      // Disable filesystem caching
      config.cache = false;
      return config;
    },
  };
  
  export default nextConfig;