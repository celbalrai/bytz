#!/usr/bin/env python3
# Copyright (c) 2014-2016 The Bitcoin Core developers
# Copyright (c) 2021 The Bytz Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test the wallet."""
import sys

from test_framework.test_framework import BytzTestFramework
from test_framework.util import *
from test_framework.blocktools import *


class WalletTest(BytzTestFramework):
    def set_test_params(self):
        self.num_nodes = 2
        self.setup_clean_chain = True
        self.extra_args = [['-sporkkey=5rE5LTDq3tRhaPW3RT1De35MocGc9wD8foaBGioxSXJsn45XaFG'],[]]

    def setup_network(self):
        self.add_nodes(2, self.extra_args, stderr=sys.stdout)
        self.start_node(0)
        self.start_node(1)
        connect_nodes_bi(self.nodes,0,1)
        self.sync_all(self.nodes[0:1])

    def run_test(self):
        self.log.info("Importing token management privkey...")
        self.nodes[0].importprivkey("5rE5LTDq3tRhaPW3RT1De35MocGc9wD8foaBGioxSXJsn45XaFG")
        privkey = self.nodes[0].dumpprivkey("TqMgq4qkw7bGxf6CDhtDfEqzEtWD5C7x8U")
        assert_equal(privkey, "5rE5LTDq3tRhaPW3RT1De35MocGc9wD8foaBGioxSXJsn45XaFG")

        self.log.info("Mining blocks...")
        self.nodes[0].generate(16)

        inputs  = [ ]
        outputs = { self.nodes[0].getnewaddress() : 15000000, self.nodes[0].getnewaddress() : 15000000, self.nodes[0].getnewaddress() : 15000000, self.nodes[0].getnewaddress() : 15000000, self.nodes[0].getnewaddress() : 15000000, self.nodes[0].getnewaddress() : 15000000 }
        rawtx = self.nodes[0].createrawtransaction(inputs, outputs)
        rawtxfund = self.nodes[0].fundrawtransaction(rawtx)['hex']
        tx = FromHex(CTransaction(), rawtxfund)
        tx_signed = self.nodes[0].signrawtransactionwithwallet(ToHex(tx))["hex"]
        self.nodes[0].sendrawtransaction(tx_signed)

        self.nodes[0].generate(300)

        self.log.info("Funding token management address...")
        self.nodes[0].sendtoaddress("TqMgq4qkw7bGxf6CDhtDfEqzEtWD5C7x8U", 1)

        self.log.info("Mining blocks...")
        self.nodes[0].generate(1)

# configuremanagementtoken MGT Management https://www.google.com 0 4 906e74f8d70d3dcadd4523c5c217360880f8b311292fcd4e39da6fd8d1fd14b36d27abe642483f2ff4c0ed492c707db9 false true
        self.log.info("Create MGT token...")
        mgtBLSKey = self.nodes[0].bls("generate")
        self.log.info("mgtBLSKey:")
        self.log.info(mgtBLSKey)
        mgtConfig = self.nodes[0].configuremanagementtoken("MGT", "Management", "4", "https://www.google.com", "4f92d91db24bb0b8ca24a2ec86c4b012ccdc4b2e9d659c2079f5cc358413a765", mgtBLSKey['public'], "false", "true")
        self.nodes[0].generate(1)
        self.log.info("mgtConfig:")
        self.log.info(mgtConfig)
        tokensaddress=self.nodes[0].getnewaddress()
        self.log.info("tokensaddress: "+tokensaddress)
        self.nodes[0].minttoken(mgtConfig['groupID'], tokensaddress, 20)
        self.nodes[0].generate(1)

        self.log.info("Create GVT token...")
        gvtBLSKey = self.nodes[0].bls("generate")
        self.log.info("gvtBLSKey:")
        self.log.info(gvtBLSKey)
        gvtConfig = self.nodes[0].configuremanagementtoken("GVT", "GuardianValidatorToken", "0", "https://www.google.com", "4f92d91db24bb0b8ca24a2ec86c4b012ccdc4b2e9d659c2079f5cc358413a765", gvtBLSKey['public'], "true", "true")
        self.nodes[0].generate(1)
        self.log.info("gvtConfig:")
        self.log.info(gvtConfig)
        self.nodes[0].minttoken(gvtConfig['groupID'], tokensaddress, 30)
        self.nodes[0].generate(1)
        GVTcreditID = self.nodes[0].getsubgroupid(gvtConfig['groupID'], "credit")
        self.log.info("GVTcreditID:")
        self.log.info(GVTcreditID)
        GCTcreditMint=self.nodes[0].minttoken(GVTcreditID, tokensaddress, 100)
        self.log.info("GCTcreditMint:")
        self.log.info(GCTcreditMint)
        self.nodes[0].generate(1)

        tokenbalance = self.nodes[0].gettokenbalance()
        self.log.info("tokenbalance:")
        self.log.info(tokenbalance)

        self.sync_all(self.nodes[0:1])

        mn01_collateral_address = self.nodes[0].getnewaddress()
        mn01_p2p_port = p2p_port(0)
        mn01_blsKey = self.nodes[0].bls('generate')
        mn01_fundsAddr = self.nodes[0].getnewaddress()
        mn01_ownerAddr = self.nodes[0].getnewaddress()
        mn01_operatorAddr = mn01_blsKey['public']
        mn01_votingAddr = mn01_ownerAddr
#        mn01_blsMnkey = mn01_blsKey['secret']

        self.nodes[0].sendtoaddress(mn01_fundsAddr, 10000000.001)
        self.nodes[0].sendtoken(GVTcreditID, mn01_fundsAddr, 1)
        self.nodes[0].generate(1)
        mn01_collateral_address = self.nodes[0].getnewaddress()
        mn01_rewards_address = self.nodes[0].getnewaddress()

        self.log.info(mn01_collateral_address)
        self.log.info('127.0.0.1:%d' % mn01_p2p_port)
        self.log.info(mn01_ownerAddr)
        self.log.info(mn01_operatorAddr)
        self.log.info(mn01_votingAddr)
        self.log.info(mn01_rewards_address)
        self.log.info(mn01_fundsAddr)

        mn01_protx_hash = self.nodes[0].protx('register_fund', mn01_collateral_address, '127.0.0.1:%d' % mn01_p2p_port, mn01_ownerAddr, mn01_operatorAddr, mn01_votingAddr, 0, mn01_rewards_address, mn01_fundsAddr)

        mn01_collateral_txid = mn01_protx_hash
        mn01_collateral_vout = -1

        rawtx = self.nodes[0].getrawtransaction(mn01_collateral_txid, 1)
        for txout in rawtx['vout']:
            if txout['value'] == Decimal(10000000):
                mn01_collateral_vout = txout['n']
                break
        assert(mn01_collateral_vout != -1)

        self.log.info("mn01_protx_hash:")
        self.log.info(mn01_protx_hash)

        self.sync_all()
        self.nodes[0].spork("SPORK_4_DIP0003_ENFORCED", self.nodes[0].getblockcount() + 1)
        self.wait_for_sporks_same()
        self.sync_all()

        self.nodes[0].generate(2)

        self.log.info(self.nodes[0].masternode('list'))

    def cutoff(self):
        self.log.info("Done")


if __name__ == '__main__':
    WalletTest().main()
