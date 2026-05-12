import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import 'react-tabs/style/react-tabs.css';

export default () => {

    <Tabs>
        <TabList>
            <tab>import</tab>
            <tab>edit</tab>
            <tab>settings</tab>
        </TabList>

        <TabPanel>
            <h2>panel 1</h2>
        </TabPanel>
        <TabPanel>
            <h2>panel 2</h2>
        </TabPanel>
    </Tabs>
    
}