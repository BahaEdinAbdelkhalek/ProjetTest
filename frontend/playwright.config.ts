import { defineConfig, devices } from '@playwright/test';
import process from 'node:process';
export default defineConfig({testDir:'./e2e',fullyParallel:false,reporter:[['html',{outputFolder:'playwright-report',open:'never'}],['list']],use:{baseURL:process.env.BASE_URL||'http://localhost:4200',trace:'retain-on-failure',screenshot:'only-on-failure'},projects:[{name:'chromium',use:{...devices['Desktop Chrome']}},{name:'firefox',use:{...devices['Desktop Firefox']}}]});
